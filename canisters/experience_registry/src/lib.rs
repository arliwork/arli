use candid::{CandidType, Deserialize, Principal};
use ic_cdk::{query, update, init};
use ic_stable_structures::{
    memory_manager::{MemoryId, MemoryManager, VirtualMemory},
    DefaultMemoryImpl, StableBTreeMap,
};
use std::cell::RefCell;

// Types
type Memory = VirtualMemory<DefaultMemoryImpl>;

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct AgentExperience {
    pub agent_id: String,
    pub agent_name: String,
    pub owner: Principal,
    pub creator: Principal,
    pub created_at: u64,
    pub total_xp: u64,
    pub level: u32,
    pub tier: String,
    pub total_tasks: u64,
    pub successful_tasks: u64,
    pub total_revenue: u64,  // in cents
    pub market_value: u64,   // in cents
    pub hourly_rate: u64,    // in cents
    pub domains: Vec<String>,
    pub achievements: Vec<String>,
    pub times_sold: u32,
    pub previous_owners: Vec<Principal>,
    pub is_listed: bool,
    pub listing_price: Option<u64>,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct TaskRecord {
    pub task_id: String,
    pub category: String,
    pub description: String,
    pub success: bool,
    pub execution_time: u64,
    pub revenue_generated: u64,
    pub client_rating: Option<u8>,
    pub timestamp: u64,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct SaleRecord {
    pub agent_id: String,
    pub seller: Principal,
    pub buyer: Principal,
    pub price: u64,
    pub timestamp: u64,
}

// State
thread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> = RefCell::new(
        MemoryManager::init(DefaultMemoryImpl::default())
    );
    
    static AGENTS: RefCell<StableBTreeMap<String, AgentExperience, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(0)))
        )
    );
    
    static TASKS: RefCell<StableBTreeMap<String, Vec<TaskRecord>, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(1)))
        )
    );
    
    static SALES: RefCell<StableBTreeMap<String, Vec<SaleRecord>, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(2)))
        )
    );
}

// NFT Standard (DIP-721 compatible)
#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct NftToken {
    pub token_id: u64,
    pub agent_id: String,
    pub owner: Principal,
    pub metadata: TokenMetadata,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct TokenMetadata {
    pub name: String,
    pub description: String,
    pub image: String,
    pub level: u32,
    pub tier: String,
    pub market_value: u64,
    pub attributes: Vec<(String, String)>,
}

// Initialize
#[init]
fn init() {
    ic_cdk::println!("Experience Registry Canister initialized");
}

// Agent Management
#[update]
fn create_agent(agent_name: String) -> Result<AgentExperience, String> {
    let caller = ic_cdk::caller();
    let agent_id = format!("agent_{}_{}", 
        caller.to_text().replace("-", ""),
        ic_cdk::api::time()
    );
    
    let agent = AgentExperience {
        agent_id: agent_id.clone(),
        agent_name,
        owner: caller,
        creator: caller,
        created_at: ic_cdk::api::time(),
        total_xp: 0,
        level: 1,
        tier: "NOVICE".to_string(),
        total_tasks: 0,
        successful_tasks: 0,
        total_revenue: 0,
        market_value: 5000,  // $50.00 in cents
        hourly_rate: 1000,   // $10.00 in cents
        domains: vec![],
        achievements: vec![],
        times_sold: 0,
        previous_owners: vec![],
        is_listed: false,
        listing_price: None,
    };
    
    AGENTS.with(|agents| {
        agents.borrow_mut().insert(agent_id, agent.clone());
    });
    
    Ok(agent)
}

#[query]
fn get_agent(agent_id: String) -> Option<AgentExperience> {
    AGENTS.with(|agents| agents.borrow().get(&agent_id).cloned())
}

#[query]
fn get_my_agents() -> Vec<AgentExperience> {
    let caller = ic_cdk::caller();
    AGENTS.with(|agents| {
        agents.borrow()
            .iter()
            .filter(|(_, agent)| agent.owner == caller)
            .map(|(_, agent)| agent.clone())
            .collect()
    })
}

// Task Recording
#[update]
fn record_task(agent_id: String, task: TaskRecord) -> Result<AgentExperience, String> {
    let caller = ic_cdk::caller();
    
    AGENTS.with(|agents| {
        let mut agents = agents.borrow_mut();
        
        if let Some(mut agent) = agents.get(&agent_id) {
            // Verify ownership
            if agent.owner != caller {
                return Err("Not authorized".to_string());
            }
            
            // Update stats
            agent.total_tasks += 1;
            if task.success {
                agent.successful_tasks += 1;
                agent.total_xp += calculate_xp(&task);
            }
            agent.total_revenue += task.revenue_generated;
            
            // Update domains
            if !agent.domains.contains(&task.category) {
                agent.domains.push(task.category.clone());
            }
            
            // Check level up
            check_level_up(&mut agent);
            
            // Recalculate market value
            agent.market_value = calculate_market_value(&agent);
            agent.hourly_rate = calculate_hourly_rate(&agent);
            
            // Store task
            TASKS.with(|tasks| {
                let mut tasks = tasks.borrow_mut();
                let agent_tasks = tasks.get(&agent_id).unwrap_or_default();
                let mut new_tasks = agent_tasks.clone();
                new_tasks.push(task);
                tasks.insert(agent_id, new_tasks);
            });
            
            agents.insert(agent.agent_id.clone(), agent.clone());
            Ok(agent)
        } else {
            Err("Agent not found".to_string())
        }
    })
}

fn calculate_xp(task: &TaskRecord) -> u64 {
    let base = 10;
    let success_bonus = 10;
    let time_bonus = (20_u64).saturating_sub(task.execution_time / 60);
    let revenue_bonus = task.revenue_generated / 100;
    let rating_bonus = task.client_rating.unwrap_or(3) as u64 * 5;
    
    base + success_bonus + time_bonus + revenue_bonus + rating_bonus
}

fn check_level_up(agent: &mut AgentExperience) {
    let xp_needed = (100.0 * ((agent.level + 1) as f64).powf(1.5)) as u64;
    
    if agent.total_xp >= xp_needed {
        agent.level += 1;
        agent.tier = match agent.level {
            1..=3 => "NOVICE".to_string(),
            4..=6 => "APPRENTICE".to_string(),
            7..=9 => "JOURNEYMAN".to_string(),
            10..=14 => "EXPERT".to_string(),
            15..=19 => "MASTER".to_string(),
            20..=24 => "GRANDMASTER".to_string(),
            _ => "LEGENDARY".to_string(),
        };
    }
}

fn calculate_market_value(agent: &AgentExperience) -> u64 {
    let base = 5000_u64;  // $50.00
    let level_multiplier = (1.5_f64.powf(agent.level as f64) * 100.0) as u64;
    let success_rate = if agent.total_tasks > 0 {
        agent.successful_tasks as f64 / agent.total_tasks as f64
    } else { 0.0 };
    let success_factor = (1.0 + success_rate * 2.0) as u64;
    
    let tier_bonus = agent.level * 10000;  // $100 per level
    let diversity_bonus = (agent.domains.len() as u64) * 5000;  // $50 per domain
    
    base * level_multiplier * success_factor / 100 + tier_bonus + diversity_bonus
}

fn calculate_hourly_rate(agent: &AgentExperience) -> u64 {
    let base_rate = 1000_u64;  // $10.00
    let exp_multiplier = (1.3_f64.powf(agent.level as f64) * 100.0) as u64;
    base_rate * exp_multiplier / 100
}

// Marketplace Functions
#[update]
fn list_agent(agent_id: String, price: u64) -> Result<AgentExperience, String> {
    let caller = ic_cdk::caller();
    
    AGENTS.with(|agents| {
        let mut agents = agents.borrow_mut();
        
        if let Some(mut agent) = agents.get(&agent_id) {
            if agent.owner != caller {
                return Err("Not authorized".to_string());
            }
            
            agent.is_listed = true;
            agent.listing_price = Some(price);
            
            agents.insert(agent_id, agent.clone());
            Ok(agent)
        } else {
            Err("Agent not found".to_string())
        }
    })
}

#[update]
fn buy_agent(agent_id: String) -> Result<AgentExperience, String> {
    let buyer = ic_cdk::caller();
    
    AGENTS.with(|agents| {
        let mut agents = agents.borrow_mut();
        
        if let Some(mut agent) = agents.get(&agent_id) {
            if !agent.is_listed {
                return Err("Agent not listed".to_string());
            }
            
            let price = agent.listing_price.unwrap();
            let seller = agent.owner;
            
            // Transfer ownership
            agent.previous_owners.push(seller);
            agent.owner = buyer;
            agent.times_sold += 1;
            agent.is_listed = false;
            agent.listing_price = None;
            
            // Record sale
            let sale = SaleRecord {
                agent_id: agent_id.clone(),
                seller,
                buyer,
                price,
                timestamp: ic_cdk::api::time(),
            };
            
            SALES.with(|sales| {
                let mut sales = sales.borrow_mut();
                let agent_sales = sales.get(&agent_id).unwrap_or_default();
                let mut new_sales = agent_sales.clone();
                new_sales.push(sale);
                sales.insert(agent_id, new_sales);
            });
            
            agents.insert(agent_id, agent.clone());
            Ok(agent)
        } else {
            Err("Agent not found".to_string())
        }
    })
}

#[query]
fn get_marketplace_listings() -> Vec<AgentExperience> {
    AGENTS.with(|agents| {
        agents.borrow()
            .iter()
            .filter(|(_, agent)| agent.is_listed)
            .map(|(_, agent)| agent.clone())
            .collect()
    })
}

// NFT Functions
#[query]
fn nft_metadata(agent_id: String) -> Option<TokenMetadata> {
    AGENTS.with(|agents| {
        agents.borrow().get(&agent_id).map(|agent| TokenMetadata {
            name: agent.agent_name.clone(),
            description: format!("Level {} {} Agent with {} tasks completed", 
                agent.level, agent.tier, agent.total_tasks),
            image: format!("https://arli.io/nft/{}", agent_id),
            level: agent.level,
            tier: agent.tier.clone(),
            market_value: agent.market_value,
            attributes: vec![
                ("Success Rate".to_string(), format!("{:.1}%", 
                    if agent.total_tasks > 0 {
                        (agent.successful_tasks as f64 / agent.total_tasks as f64) * 100.0
                    } else { 0.0 })),
                ("Total Revenue".to_string(), format!("${:.2}", agent.total_revenue as f64 / 100.0)),
                ("Domains".to_string(), agent.domains.join(", ")),
                ("Times Sold".to_string(), agent.times_sold.to_string()),
            ],
        })
    })
}

#[query]
fn get_agent_history(agent_id: String) -> Option<(Vec<TaskRecord>, Vec<SaleRecord>)> {
    let tasks = TASKS.with(|t| t.borrow().get(&agent_id).cloned()).unwrap_or_default();
    let sales = SALES.with(|s| s.borrow().get(&agent_id).cloned()).unwrap_or_default();
    Some((tasks, sales))
}

#[query]
fn get_global_stats() -> (u64, u64, u64) {
    AGENTS.with(|agents| {
        let agents = agents.borrow();
        let total_agents = agents.len() as u64;
        let total_value: u64 = agents.iter().map(|(_, a)| a.market_value).sum();
        let total_revenue: u64 = agents.iter().map(|(_, a)| a.total_revenue).sum();
        (total_agents, total_value, total_revenue)
    })
}

// Export Candid
ic_cdk::export_candid!();
