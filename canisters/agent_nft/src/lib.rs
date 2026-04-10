use candid::{CandidType, Deserialize, Principal, Nat};
use ic_cdk::{query, update, init};
use ic_stable_structures::{
    memory_manager::{MemoryId, MemoryManager, VirtualMemory},
    DefaultMemoryImpl, StableBTreeMap, StableCell,
};
use std::cell::RefCell;
use std::collections::HashMap;

// DIP-721 Standard Implementation for Agent NFTs
type Memory = VirtualMemory<DefaultMemoryImpl>;

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct TokenMetadata {
    pub token_uri: String,
    pub name: String,
    pub description: String,
    pub image: String,
    pub attributes: Vec<Trait>,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct Trait {
    pub trait_type: String,
    pub value: String,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct TokenInfo {
    pub token_id: Nat,
    pub owner: Principal,
    pub metadata: TokenMetadata,
    pub agent_id: String,
    pub level: u32,
    pub tier: String,
    pub market_value: u64,
    pub minted_at: u64,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct ApprovalInfo {
    pub approved: Principal,
    pub token_id: Nat,
}

// State	hread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> = RefCell::new(
        MemoryManager::init(DefaultMemoryImpl::default())
    );
    
    // Token storage
    static TOKENS: RefCell<StableBTreeMap<Nat, TokenInfo, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(0)))
        )
    );
    
    // Owner -> tokens mapping
    static OWNER_TOKENS: RefCell<StableBTreeMap<Principal, Vec<Nat>, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(1)))
        )
    );
    
    // Approvals: token_id -> approved principal
    static APPROVALS: RefCell<StableBTreeMap<Nat, Principal, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(2)))
        )
    );
    
    // Operator approvals: owner -> operator -> bool
    static OPERATOR_APPROVALS: RefCell<StableBTreeMap<(Principal, Principal), bool, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(3)))
        )
    );
    
    // Token counter
    static TOKEN_COUNTER: RefCell<StableCell<Nat, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(4))),
            Nat::from(0u64)
        ).expect("Failed to init token counter")
    );
    
    // Sale history
    static SALE_HISTORY: RefCell<StableBTreeMap<String, Vec<SaleRecord>, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(5)))
        )
    );
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct SaleRecord {
    pub token_id: Nat,
    pub seller: Principal,
    pub buyer: Principal,
    pub price: u64,
    pub timestamp: u64,
}

// DIP-721 Events
#[derive(CandidType, Deserialize, Clone, Debug)]
pub enum Event {
    Mint {
        token_id: Nat,
        to: Principal,
        agent_id: String,
    },
    Transfer {
        from: Principal,
        to: Principal,
        token_id: Nat,
    },
    Approval {
        owner: Principal,
        approved: Principal,
        token_id: Nat,
    },
    ApprovalForAll {
        owner: Principal,
        operator: Principal,
        approved: bool,
    },
}

// Initialize
#[init]
fn init() {
    ic_cdk::println!("Agent NFT Canister initialized");
}

// DIP-721 Core Functions

/// Mint new NFT for an agent
#[update]
fn mint(
    to: Principal,
    metadata: TokenMetadata,
    agent_id: String,
    level: u32,
    tier: String,
    market_value: u64,
) -> Result<Nat, String> {
    let caller = ic_cdk::caller();
    
    // Only experience registry canister should mint
    // TODO: Add proper authorization check
    
    let token_id = TOKEN_COUNTER.with(|counter| {
        let current = counter.borrow().get().clone();
        let next = Nat::from(current.0.to_u64().unwrap() + 1);
        counter.borrow_mut().set(next.clone()).expect("Failed to increment counter");
        next
    });
    
    let token_info = TokenInfo {
        token_id: token_id.clone(),
        owner: to,
        metadata,
        agent_id,
        level,
        tier,
        market_value,
        minted_at: ic_cdk::api::time(),
    };
    
    // Store token
    TOKENS.with(|tokens| {
        tokens.borrow_mut().insert(token_id.clone(), token_info);
    });
    
    // Update owner mapping
    OWNER_TOKENS.with(|owner_tokens| {
        let mut owner_tokens = owner_tokens.borrow_mut();
        let mut tokens = owner_tokens.get(&to).unwrap_or_default();
        tokens.push(token_id.clone());
        owner_tokens.insert(to, tokens);
    });
    
    // Log event
    ic_cdk::println!("Minted token {} for {}", token_id.0, to.to_text());
    
    Ok(token_id)
}

/// Get owner of a token
#[query]
fn owner_of(token_id: Nat) -> Option<Principal> {
    TOKENS.with(|tokens| {
        tokens.borrow().get(&token_id).map(|t| t.owner)
    })
}

/// Transfer token
#[update]
fn transfer_from(from: Principal, to: Principal, token_id: Nat) -> Result<(), String> {
    let caller = ic_cdk::caller();
    
    // Check authorization
    let is_authorized = is_approved_or_owner(caller, from, token_id.clone());
    if !is_authorized {
        return Err("Not authorized to transfer".to_string());
    }
    
    // Perform transfer
    TOKENS.with(|tokens| {
        let mut tokens = tokens.borrow_mut();
        if let Some(mut token) = tokens.get(&token_id) {
            if token.owner != from {
                return Err("From address is not owner".to_string());
            }
            
            // Update token owner
            token.owner = to;
            tokens.insert(token_id.clone(), token);
            
            // Update owner mappings
            update_owner_tokens(from, to, token_id.clone());
            
            // Clear approvals
            APPROVALS.with(|approvals| {
                approvals.borrow_mut().remove(&token_id);
            });
            
            Ok(())
        } else {
            Err("Token not found".to_string())
        }
    })
}

/// Approve address to spend token
#[update]
fn approve(approved: Principal, token_id: Nat) -> Result<(), String> {
    let caller = ic_cdk::caller();
    
    let is_owner = TOKENS.with(|tokens| {
        tokens.borrow().get(&token_id).map(|t| t.owner == caller).unwrap_or(false)
    });
    
    if !is_owner {
        return Err("Not token owner".to_string());
    }
    
    APPROVALS.with(|approvals| {
        approvals.borrow_mut().insert(token_id, approved);
    });
    
    Ok(())
}

/// Get approved address for token
#[query]
fn get_approved(token_id: Nat) -> Option<Principal> {
    APPROVALS.with(|approvals| approvals.borrow().get(&token_id))
}

/// Set approval for all tokens
#[update]
fn set_approval_for_all(operator: Principal, approved: bool) -> Result<(), String> {
    let caller = ic_cdk::caller();
    
    if caller == operator {
        return Err("Cannot approve self".to_string());
    }
    
    OPERATOR_APPROVALS.with(|ops| {
        if approved {
            ops.borrow_mut().insert((caller, operator), true);
        } else {
            ops.borrow_mut().remove(&(caller, operator));
        }
    });
    
    Ok(())
}

/// Check if operator is approved for all
#[query]
fn is_approved_for_all(owner: Principal, operator: Principal) -> bool {
    OPERATOR_APPROVALS.with(|ops| {
        ops.borrow().get(&(owner, operator)).unwrap_or(false)
    })
}

/// Get token metadata
#[query]
fn token_metadata(token_id: Nat) -> Option<TokenMetadata> {
    TOKENS.with(|tokens| {
        tokens.borrow().get(&token_id).map(|t| t.metadata.clone())
    })
}

/// Get full token info
#[query]
fn get_token_info(token_id: Nat) -> Option<TokenInfo> {
    TOKENS.with(|tokens| tokens.borrow().get(&token_id).cloned())
}

/// Get all tokens owned by address
#[query]
fn tokens_of(owner: Principal) -> Vec<Nat> {
    OWNER_TOKENS.with(|owner_tokens| {
        owner_tokens.borrow().get(&owner).unwrap_or_default()
    })
}

/// Get total supply
#[query]
fn total_supply() -> Nat {
    TOKEN_COUNTER.with(|counter| counter.borrow().get().clone())
}

/// Get all tokens (paginated)
#[query]
fn get_all_tokens(start: usize, limit: usize) -> Vec<TokenInfo> {
    TOKENS.with(|tokens| {
        tokens.borrow()
            .iter()
            .skip(start)
            .take(limit)
            .map(|(_, token)| token.clone())
            .collect()
    })
}

// Sale Functions

#[update]
fn record_sale(
    token_id: Nat,
    seller: Principal,
    buyer: Principal,
    price: u64,
) -> Result<(), String> {
    let sale = SaleRecord {
        token_id,
        seller,
        buyer,
        price,
        timestamp: ic_cdk::api::time(),
    };
    
    TOKENS.with(|tokens| {
        if let Some(token) = tokens.borrow().get(&sale.token_id) {
            SALE_HISTORY.with(|history| {
                let mut history = history.borrow_mut();
                let agent_history = history.get(&token.agent_id).unwrap_or_default();
                let mut new_history = agent_history.clone();
                new_history.push(sale);
                history.insert(token.agent_id, new_history);
            });
        }
    });
    
    Ok(())
}

#[query]
fn get_sale_history(agent_id: String) -> Vec<SaleRecord> {
    SALE_HISTORY.with(|history| {
        history.borrow().get(&agent_id).unwrap_or_default()
    })
}

// Helper functions

fn is_approved_or_owner(caller: Principal, owner: Principal, token_id: Nat) -> bool {
    if caller == owner {
        return true;
    }
    
    // Check token approval
    let token_approved = APPROVALS.with(|approvals| {
        approvals.borrow().get(&token_id) == Some(caller)
    });
    
    if token_approved {
        return true;
    }
    
    // Check operator approval
    is_approved_for_all(owner, caller)
}

fn update_owner_tokens(from: Principal, to: Principal, token_id: Nat) {
    OWNER_TOKENS.with(|owner_tokens| {
        let mut owner_tokens = owner_tokens.borrow_mut();
        
        // Remove from old owner
        if let Some(mut tokens) = owner_tokens.get(&from) {
            tokens.retain(|t| t != &token_id);
            owner_tokens.insert(from, tokens);
        }
        
        // Add to new owner
        let mut to_tokens = owner_tokens.get(&to).unwrap_or_default();
        to_tokens.push(token_id);
        owner_tokens.insert(to, to_tokens);
    });
}

// Metadata for OpenSea/ICRC-7 compatibility

#[query]
fn name() -> String {
    "ARLI Agent NFTs".to_string()
}

#[query]
fn symbol() -> String {
    "ARLI".to_string()
}

#[query]
fn description() -> String {
    "Trained AI agents as transferable NFTs with proven experience and revenue history".to_string()
}

// Export Candid
ic_cdk::export_candid!();
