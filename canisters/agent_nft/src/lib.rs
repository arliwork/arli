use candid::{CandidType, Deserialize, Principal, Nat, Encode, Decode};
use ic_cdk::{query, update, init};
use ic_stable_structures::{
    memory_manager::{MemoryId, MemoryManager, VirtualMemory},
    DefaultMemoryImpl, StableBTreeMap, StableCell, Storable,
};
use std::borrow::Cow;
use std::cell::RefCell;

// DIP-721 Standard Implementation for Agent NFTs
type Memory = VirtualMemory<DefaultMemoryImpl>;

// ─── Storable helpers ───────────────────────────────────────────────

fn to_bytes<T: CandidType>(value: &T) -> Cow<[u8]> {
    Cow::Owned(Encode!(value).expect("encode failed"))
}

fn from_bytes<T: CandidType + for<'de> Deserialize<'de>>(bytes: Cow<[u8]>) -> T {
    Decode!(&bytes, T).expect("decode failed")
}

impl Storable for TokenMetadata {
    fn to_bytes(&self) -> Cow<[u8]> {
        to_bytes(self)
    }
    fn from_bytes(bytes: Cow<[u8]>) -> Self {
        from_bytes(bytes)
    }
    const BOUND: ic_stable_structures::storable::Bound =
        ic_stable_structures::storable::Bound::Unbounded;
}

impl Storable for TokenInfo {
    fn to_bytes(&self) -> Cow<[u8]> {
        to_bytes(self)
    }
    fn from_bytes(bytes: Cow<[u8]>) -> Self {
        from_bytes(bytes)
    }
    const BOUND: ic_stable_structures::storable::Bound =
        ic_stable_structures::storable::Bound::Unbounded;
}

impl Storable for SaleRecord {
    fn to_bytes(&self) -> Cow<[u8]> {
        to_bytes(self)
    }
    fn from_bytes(bytes: Cow<[u8]>) -> Self {
        from_bytes(bytes)
    }
    const BOUND: ic_stable_structures::storable::Bound =
        ic_stable_structures::storable::Bound::Unbounded;
}

// ─── Types ───────────────────────────────────────────────────────────

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct Trait {
    pub trait_type: String,
    pub value: String,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct TokenMetadata {
    pub token_uri: String,
    pub name: String,
    pub description: String,
    pub image: String,
    pub attributes: Vec<Trait>,
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
pub struct SaleRecord {
    pub token_id: Nat,
    pub seller: Principal,
    pub buyer: Principal,
    pub price: u64,
    pub timestamp: u64,
}

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

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct CollectionInfo {
    pub name: String,
    pub symbol: String,
    pub description: String,
    pub total_supply: Nat,
    pub logo: String,
}

// ─── State ───────────────────────────────────────────────────────────

thread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> = RefCell::new(
        MemoryManager::init(DefaultMemoryImpl::default())
    );

    // Token storage: token_id -> TokenInfo
    static TOKENS: RefCell<StableBTreeMap<u64, TokenInfo, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(0)))
        )
    );

    // Owner -> token_ids mapping (stored as comma-separated u64 string for simplicity)
    static OWNER_TOKENS: RefCell<StableBTreeMap<Principal, String, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(1)))
        )
    );

    // Single-token approvals: token_id -> approved principal
    static APPROVALS: RefCell<StableBTreeMap<u64, Principal, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(2)))
        )
    );

    // Operator approvals: (owner, operator) -> bool
    static OPERATOR_APPROVALS: RefCell<StableBTreeMap<(Principal, Principal), bool, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(3)))
        )
    );

    // Token counter (next token_id)
    static TOKEN_COUNTER: RefCell<StableCell<u64, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(4))),
            0u64
        ).expect("Failed to init token counter")
    );

    // Sale history per agent_id (stored as JSON string)
    static SALE_HISTORY: RefCell<StableBTreeMap<String, String, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(5)))
        )
    );

    // Admin / authorized minters
    static ADMINS: RefCell<StableBTreeMap<Principal, bool, Memory>> = RefCell::new(
        StableBTreeMap::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(6)))
        )
    );

    // Events log (in-memory, not stable)
    static EVENTS: RefCell<Vec<Event>> = RefCell::new(Vec::new());
}

// ─── Owner tokens helpers ───────────────────────────────────────────

fn get_owner_tokens(owner: Principal) -> Vec<u64> {
    OWNER_TOKENS.with(|ot| {
        ot.borrow().get(&owner)
            .map(|s| {
                if s.is_empty() {
                    Vec::new()
                } else {
                    s.split(',')
                        .filter_map(|x| x.parse::<u64>().ok())
                        .collect()
                }
            })
            .unwrap_or_default()
    })
}

fn set_owner_tokens(owner: Principal, tokens: Vec<u64>) {
    OWNER_TOKENS.with(|ot| {
        let s = tokens.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
        ot.borrow_mut().insert(owner, s);
    });
}

// ─── Sale history helpers ───────────────────────────────────────────
fn get_sale_records(agent_id: &String) -> Vec<SaleRecord> {
    SALE_HISTORY.with(|sh| {
        sh.borrow()
            .get(agent_id)
            .and_then(|s| Decode!(&s.into_bytes(), Vec<SaleRecord>).ok())
            .unwrap_or_default()
    })
}

fn set_sale_records(agent_id: &String, records: Vec<SaleRecord>) {
    SALE_HISTORY.with(|sh| {
        if let Ok(bytes) = Encode!(&records) {
            sh.borrow_mut().insert(agent_id.clone(), String::from_utf8_lossy(&bytes).to_string());
        }
    });
}

// ─── Initialization ─────────────────────────────────────────────────

#[init]
fn init() {
    let caller = ic_cdk::caller();
    ADMINS.with(|admins| {
        admins.borrow_mut().insert(caller, true);
    });
    ic_cdk::println!("Agent NFT Canister initialized. Admin: {}", caller.to_text());
}

// ─── Admin helpers ──────────────────────────────────────────────────

fn is_admin(caller: Principal) -> bool {
    ADMINS.with(|admins| admins.borrow().get(&caller).unwrap_or(false))
}

fn assert_admin() -> Result<(), String> {
    let caller = ic_cdk::caller();
    if is_admin(caller) {
        Ok(())
    } else {
        Err("Unauthorized: admin only".to_string())
    }
}

fn is_approved_or_owner(caller: Principal, owner: Principal, token_id: u64) -> bool {
    if caller == owner {
        return true;
    }
    // Check single-token approval
    let token_approved = APPROVALS.with(|a| a.borrow().get(&token_id));
    if token_approved == Some(caller) {
        return true;
    }
    // Check operator approval
    OPERATOR_APPROVALS.with(|ops| {
        ops.borrow().get(&(owner, caller)).unwrap_or(false)
    })
}

fn assert_owner_or_approved(token_id: u64) -> Result<Principal, String> {
    let caller = ic_cdk::caller();
    let owner = TOKENS.with(|t| {
        t.borrow().get(&token_id).map(|info| info.owner)
    });
    match owner {
        Some(o) => {
            if is_approved_or_owner(caller, o, token_id) {
                Ok(o)
            } else {
                Err("Not owner nor approved".to_string())
            }
        }
        None => Err("Token does not exist".to_string()),
    }
}

// ─── DIP-721 Core ───────────────────────────────────────────────────

/// Mint a new Agent NFT.
/// Only admins / authorized minters can call.
#[update]
fn mint(
    to: Principal,
    metadata: TokenMetadata,
    agent_id: String,
    level: u32,
    tier: String,
    market_value: u64,
) -> Result<Nat, String> {
    assert_admin()?;

    let token_id_u64 = TOKEN_COUNTER.with(|counter| {
        let current = *counter.borrow().get();
        let next = current + 1;
        counter.borrow_mut().set(next).expect("increment counter");
        next
    });

    let token_info = TokenInfo {
        token_id: Nat::from(token_id_u64),
        owner: to,
        metadata,
        agent_id: agent_id.clone(),
        level,
        tier,
        market_value,
        minted_at: ic_cdk::api::time(),
    };

    TOKENS.with(|tokens| {
        tokens.borrow_mut().insert(token_id_u64, token_info);
    });

    let mut list = get_owner_tokens(to);
    list.push(token_id_u64);
    set_owner_tokens(to, list);

    EVENTS.with(|ev| {
        ev.borrow_mut().push(Event::Mint {
            token_id: Nat::from(token_id_u64),
            to,
            agent_id,
        });
    });

    ic_cdk::println!("Minted token {} for {}", token_id_u64, to.to_text());
    Ok(Nat::from(token_id_u64))
}

#[query]
fn balance_of(owner: Principal) -> Nat {
    let list = get_owner_tokens(owner);
    Nat::from(list.len() as u64)
}

#[query]
fn owner_of(token_id: Nat) -> Option<Principal> {
    let id: u64 = token_id.0.try_into().ok()?;
    TOKENS.with(|t| t.borrow().get(&id).map(|info| info.owner))
}

#[query]
fn owner_token_ids(owner: Principal) -> Vec<Nat> {
    get_owner_tokens(owner)
        .into_iter()
        .map(Nat::from)
        .collect()
}

#[update]
fn transfer_from(from: Principal, to: Principal, token_id: Nat) -> Result<(), String> {
    let caller = ic_cdk::caller();
    let id: u64 = token_id.0.try_into().map_err(|_| "Invalid token_id")?;

    let owner = TOKENS.with(|t| t.borrow().get(&id).map(|info| info.owner));
    let owner = owner.ok_or("Token does not exist")?;
    if owner != from {
        return Err("From address is not owner".to_string());
    }
    if !is_approved_or_owner(caller, from, id) {
        return Err("Not authorized to transfer".to_string());
    }

    // Update token owner
    TOKENS.with(|t| {
        let mut map = t.borrow_mut();
        if let Some(mut info) = map.get(&id) {
            info.owner = to;
            map.insert(id, info);
        }
    });

    // Update owner mappings
    let mut from_list = get_owner_tokens(from);
    from_list.retain(|&x| x != id);
    set_owner_tokens(from, from_list);

    let mut to_list = get_owner_tokens(to);
    to_list.push(id);
    set_owner_tokens(to, to_list);

    // Clear single-token approval
    APPROVALS.with(|a| {
        a.borrow_mut().remove(&id);
    });

    EVENTS.with(|ev| {
        ev.borrow_mut().push(Event::Transfer {
            from,
            to,
            token_id: Nat::from(id),
        });
    });

    Ok(())
}

#[update]
fn approve(approved: Principal, token_id: Nat) -> Result<(), String> {
    let caller = ic_cdk::caller();
    let id: u64 = token_id.0.try_into().map_err(|_| "Invalid token_id")?;

    let is_owner = TOKENS.with(|t| {
        t.borrow().get(&id).map(|info| info.owner == caller).unwrap_or(false)
    });
    if !is_owner {
        return Err("Not token owner".to_string());
    }

    APPROVALS.with(|a| {
        a.borrow_mut().insert(id, approved);
    });

    EVENTS.with(|ev| {
        ev.borrow_mut().push(Event::Approval {
            owner: caller,
            approved,
            token_id: Nat::from(id),
        });
    });

    Ok(())
}

#[query]
fn get_approved(token_id: Nat) -> Option<Principal> {
    let id: u64 = token_id.0.try_into().ok()?;
    APPROVALS.with(|a| a.borrow().get(&id))
}

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

    EVENTS.with(|ev| {
        ev.borrow_mut().push(Event::ApprovalForAll {
            owner: caller,
            operator,
            approved,
        });
    });

    Ok(())
}

#[query]
fn is_approved_for_all(owner: Principal, operator: Principal) -> bool {
    OPERATOR_APPROVALS.with(|ops| {
        ops.borrow().get(&(owner, operator)).unwrap_or(false)
    })
}

// ─── Metadata ───────────────────────────────────────────────────────

#[query]
fn token_metadata(token_id: Nat) -> Option<TokenMetadata> {
    let id: u64 = token_id.0.try_into().ok()?;
    TOKENS.with(|t| t.borrow().get(&id).map(|info| info.metadata.clone()))
}

#[query]
fn get_token_info(token_id: Nat) -> Option<TokenInfo> {
    let id: u64 = token_id.0.try_into().ok()?;
    TOKENS.with(|t| t.borrow().get(&id).map(|x| x.clone()))
}

#[query]
fn tokens_of(owner: Principal) -> Vec<Nat> {
    owner_token_ids(owner)
}

#[query]
fn total_supply() -> Nat {
    TOKEN_COUNTER.with(|c| Nat::from(*c.borrow().get()))
}

#[query]
fn get_all_tokens(start: usize, limit: usize) -> Vec<TokenInfo> {
    TOKENS.with(|t| {
        t.borrow()
            .iter()
            .skip(start)
            .take(limit)
            .map(|(_, info)| info.clone())
            .collect()
    })
}

#[query]
fn get_collection_info() -> CollectionInfo {
    CollectionInfo {
        name: "ARLI Agent NFTs".to_string(),
        symbol: "ARLI".to_string(),
        description: "Trained AI agents as transferable NFTs with proven experience and revenue history".to_string(),
        total_supply: total_supply(),
        logo: "https://arli.io/logo.png".to_string(),
    }
}

#[query]
fn supported_interfaces() -> Vec<String> {
    vec![
        "DIP-721".to_string(),
        "DIP-721-v2".to_string(),
    ]
}

// ─── Sales ──────────────────────────────────────────────────────────

#[update]
fn record_sale(
    token_id: Nat,
    seller: Principal,
    buyer: Principal,
    price: u64,
) -> Result<(), String> {
    // Only admins can record sales (called by marketplace canister or backend)
    assert_admin()?;

    let id: u64 = token_id.0.clone().try_into().map_err(|_| "Invalid token_id")?;
    let agent_id = TOKENS.with(|t| t.borrow().get(&id).map(|info| info.agent_id.clone()));

    if let Some(agent_id) = agent_id {
        let mut history = get_sale_records(&agent_id);
        history.push(SaleRecord {
            token_id,
            seller,
            buyer,
            price,
            timestamp: ic_cdk::api::time(),
        });
        set_sale_records(&agent_id, history);
    }

    Ok(())
}

#[query]
fn get_sale_history(agent_id: String) -> Vec<SaleRecord> {
    get_sale_records(&agent_id)
}

// ─── Admin ──────────────────────────────────────────────────────────

#[update]
fn add_admin(principal: Principal) -> Result<(), String> {
    assert_admin()?;
    ADMINS.with(|a| {
        a.borrow_mut().insert(principal, true);
    });
    Ok(())
}

#[update]
fn remove_admin(principal: Principal) -> Result<(), String> {
    assert_admin()?;
    let caller = ic_cdk::caller();
    if principal == caller {
        return Err("Cannot remove yourself".to_string());
    }
    ADMINS.with(|a| {
        a.borrow_mut().remove(&principal);
    });
    Ok(())
}

#[query]
fn get_admins() -> Vec<Principal> {
    ADMINS.with(|a| {
        a.borrow()
            .iter()
            .filter(|(_, v)| *v)
            .map(|(k, _)| k)
            .collect()
    })
}

// ─── Events ─────────────────────────────────────────────────────────

#[query]
fn get_events() -> Vec<Event> {
    EVENTS.with(|ev| ev.borrow().clone())
}

// ─── Candid export ──────────────────────────────────────────────────

ic_cdk::export_candid!();
