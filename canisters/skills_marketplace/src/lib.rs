use candid::{CandidType, Deserialize, Principal, Nat, Encode, Decode};
use ic_cdk::{query, update, init};
use ic_stable_structures::{
    memory_manager::{MemoryId, MemoryManager, VirtualMemory},
    DefaultMemoryImpl, StableBTreeMap, StableCell, Storable,
};
use std::borrow::Cow;
use std::cell::RefCell;

type Memory = VirtualMemory<DefaultMemoryImpl>;

// ─── Storable helpers ───────────────────────────────────────────────

fn to_bytes<T: CandidType>(value: &T) -> Cow<[u8]> {
    Cow::Owned(candid::Encode!(value).expect("encode failed"))
}

fn from_bytes<T: CandidType + for<'de> Deserialize<'de>>(bytes: Cow<[u8]>) -> T {
    candid::Decode!(&bytes, T).expect("decode failed")
}

impl Storable for SkillListing {
    fn to_bytes(&self) -> Cow<[u8]> { to_bytes(self) }
    fn from_bytes(bytes: Cow<[u8]>) -> Self { from_bytes(bytes) }
    const BOUND: ic_stable_structures::storable::Bound =
        ic_stable_structures::storable::Bound::Unbounded;
}

impl Storable for PurchaseRecord {
    fn to_bytes(&self) -> Cow<[u8]> { to_bytes(self) }
    fn from_bytes(bytes: Cow<[u8]>) -> Self { from_bytes(bytes) }
    const BOUND: ic_stable_structures::storable::Bound =
        ic_stable_structures::storable::Bound::Unbounded;
}

// ─── Types ───────────────────────────────────────────────────────────

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct SkillListing {
    pub id: String,
    pub name: String,
    pub description: String,
    pub creator: Principal,
    pub price: u64, // in cents / smallest unit
    pub category: String,
    pub tags: Vec<String>,
    pub rating_sum: u64,
    pub rating_count: u64,
    pub purchase_count: u64,
    pub created_at: u64,
    pub is_active: bool,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct PurchaseRecord {
    pub purchase_id: String,
    pub skill_id: String,
    pub buyer: Principal,
    pub seller: Principal,
    pub price: u64,
    pub platform_fee: u64,
    pub creator_royalty: u64,
    pub timestamp: u64,
}

#[derive(CandidType, Deserialize, Clone, Debug)]
pub struct MarketplaceStats {
    pub total_listings: Nat,
    pub total_purchases: Nat,
    pub total_volume: u64,
    pub platform_revenue: u64,
}

// ─── State ───────────────────────────────────────────────────────────

thread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> = RefCell::new(
        MemoryManager::init(DefaultMemoryImpl::default())
    );

    static LISTINGS: RefCell<StableBTreeMap<String, SkillListing, Memory>> = RefCell::new(
        StableBTreeMap::init(MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(0))))
    );

    static PURCHASES: RefCell<StableBTreeMap<String, PurchaseRecord, Memory>> = RefCell::new(
        StableBTreeMap::init(MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(1))))
    );

    static LISTING_COUNTER: RefCell<StableCell<u64, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(2))),
            0u64
        ).expect("init counter")
    );

    static PURCHASE_COUNTER: RefCell<StableCell<u64, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(3))),
            0u64
        ).expect("init counter")
    );

    static PLATFORM_REVENUE: RefCell<StableCell<u64, Memory>> = RefCell::new(
        StableCell::init(
            MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(4))),
            0u64
        ).expect("init revenue")
    );

    static ADMINS: RefCell<StableBTreeMap<Principal, bool, Memory>> = RefCell::new(
        StableBTreeMap::init(MEMORY_MANAGER.with(|m| m.borrow().get(MemoryId::new(5))))
    );
}

// ─── Init ────────────────────────────────────────────────────────────

#[init]
fn init() {
    let caller = ic_cdk::caller();
    ADMINS.with(|a| a.borrow_mut().insert(caller, true));
}

fn assert_admin() -> Result<(), String> {
    let caller = ic_cdk::caller();
    let ok = ADMINS.with(|a| a.borrow().get(&caller).unwrap_or(false));
    if ok { Ok(()) } else { Err("Unauthorized".to_string()) }
}

// ─── Listings ───────────────────────────────────────────────────────

#[update]
fn create_listing(
    name: String,
    description: String,
    price: u64,
    category: String,
    tags: Vec<String>,
) -> Result<SkillListing, String> {
    let creator = ic_cdk::caller();
    let id = LISTING_COUNTER.with(|c| {
        let n = *c.borrow().get() + 1;
        c.borrow_mut().set(n).unwrap();
        n
    });

    let listing = SkillListing {
        id: format!("skill-{}", id),
        name,
        description,
        creator,
        price,
        category,
        tags,
        rating_sum: 0,
        rating_count: 0,
        purchase_count: 0,
        created_at: ic_cdk::api::time(),
        is_active: true,
    };

    LISTINGS.with(|l| l.borrow_mut().insert(listing.id.clone(), listing.clone()));
    Ok(listing)
}

#[query]
fn get_listing(id: String) -> Option<SkillListing> {
    LISTINGS.with(|l| l.borrow().get(&id))
}

#[query]
fn get_all_listings(start: usize, limit: usize) -> Vec<SkillListing> {
    LISTINGS.with(|l| {
        l.borrow().iter()
            .skip(start)
            .take(limit)
            .map(|(_, v)| v.clone())
            .collect()
    })
}

#[query]
fn get_listings_by_category(category: String) -> Vec<SkillListing> {
    LISTINGS.with(|l| {
        l.borrow().iter()
            .filter(|(_, v)| v.category == category && v.is_active)
            .map(|(_, v)| v.clone())
            .collect()
    })
}

#[query]
fn search_listings(query: String) -> Vec<SkillListing> {
    let q = query.to_lowercase();
    LISTINGS.with(|l| {
        l.borrow().iter()
            .filter(|(_, v)| {
                v.is_active && (
                    v.name.to_lowercase().contains(&q) ||
                    v.description.to_lowercase().contains(&q) ||
                    v.tags.iter().any(|t| t.to_lowercase().contains(&q))
                )
            })
            .map(|(_, v)| v.clone())
            .collect()
    })
}

#[update]
fn update_listing(id: String, price: Option<u64>, is_active: Option<bool>) -> Result<(), String> {
    let caller = ic_cdk::caller();
    LISTINGS.with(|l| {
        let mut map = l.borrow_mut();
        if let Some(mut listing) = map.get(&id) {
            if listing.creator != caller {
                return Err("Not creator".to_string());
            }
            if let Some(p) = price { listing.price = p; }
            if let Some(a) = is_active { listing.is_active = a; }
            map.insert(id, listing);
            Ok(())
        } else {
            Err("Listing not found".to_string())
        }
    })
}

// ─── Purchases ──────────────────────────────────────────────────────

#[update]
fn record_purchase(
    skill_id: String,
    buyer: Principal,
    price: u64,
) -> Result<PurchaseRecord, String> {
    assert_admin()?; // Called by backend/API after payment verification

    let listing = LISTINGS.with(|l| l.borrow().get(&skill_id));
    let listing = listing.ok_or("Listing not found")?;
    if !listing.is_active {
        return Err("Listing inactive".to_string());
    }

    let purchase_id = PURCHASE_COUNTER.with(|c| {
        let n = *c.borrow().get() + 1;
        c.borrow_mut().set(n).unwrap();
        format!("purchase-{}", n)
    });

    let platform_fee = price / 10; // 10%
    let creator_royalty = price / 20; // 5%

    let record = PurchaseRecord {
        purchase_id: purchase_id.clone(),
        skill_id: skill_id.clone(),
        buyer,
        seller: listing.creator,
        price,
        platform_fee,
        creator_royalty,
        timestamp: ic_cdk::api::time(),
    };

    PURCHASES.with(|p| p.borrow_mut().insert(purchase_id.clone(), record.clone()));

    // Update listing stats
    LISTINGS.with(|l| {
        let mut map = l.borrow_mut();
        if let Some(mut listing) = map.get(&skill_id) {
            listing.purchase_count += 1;
            map.insert(skill_id, listing);
        }
    });

    // Update platform revenue
    PLATFORM_REVENUE.with(|r| {
        let mut cell = r.borrow_mut();
        let current = *cell.get();
        cell.set(current + platform_fee).unwrap();
    });

    Ok(record)
}

#[query]
fn get_purchase(id: String) -> Option<PurchaseRecord> {
    PURCHASES.with(|p| p.borrow().get(&id))
}

#[query]
fn get_purchases_by_buyer(buyer: Principal) -> Vec<PurchaseRecord> {
    PURCHASES.with(|p| {
        p.borrow().iter()
            .filter(|(_, v)| v.buyer == buyer)
            .map(|(_, v)| v.clone())
            .collect()
    })
}

#[query]
fn get_purchases_by_seller(seller: Principal) -> Vec<PurchaseRecord> {
    PURCHASES.with(|p| {
        p.borrow().iter()
            .filter(|(_, v)| v.seller == seller)
            .map(|(_, v)| v.clone())
            .collect()
    })
}

// ─── Stats ──────────────────────────────────────────────────────────

#[query]
fn get_stats() -> MarketplaceStats {
    let total_listings = LISTINGS.with(|l| l.borrow().len());
    let total_purchases = PURCHASES.with(|p| p.borrow().len());
    let total_volume = PURCHASES.with(|p| {
        p.borrow().iter().map(|(_, v)| v.price).sum()
    });
    let platform_revenue = PLATFORM_REVENUE.with(|r| *r.borrow().get());

    MarketplaceStats {
        total_listings: Nat::from(total_listings),
        total_purchases: Nat::from(total_purchases),
        total_volume,
        platform_revenue,
    }
}

// ─── Admin ──────────────────────────────────────────────────────────

#[update]
fn add_admin(principal: Principal) -> Result<(), String> {
    assert_admin()?;
    ADMINS.with(|a| a.borrow_mut().insert(principal, true));
    Ok(())
}

#[update]
fn remove_admin(principal: Principal) -> Result<(), String> {
    assert_admin()?;
    if principal == ic_cdk::caller() {
        return Err("Cannot remove self".to_string());
    }
    ADMINS.with(|a| a.borrow_mut().remove(&principal));
    Ok(())
}

ic_cdk::export_candid!();
