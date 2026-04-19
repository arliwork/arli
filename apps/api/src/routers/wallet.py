"""Wallet routes for ICP balance and transactions"""
from fastapi import APIRouter

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/balance")
async def wallet_balance(principal: str):
    """Get ICP balance for a principal"""
    try:
        from icp_integration import icp_client
        balance_e8s = await icp_client.check_balance(principal)
        return {"balance_icp": balance_e8s / 100_000_000, "balance_e8s": balance_e8s}
    except Exception as e:
        return {"balance_icp": 0, "balance_e8s": 0, "note": str(e)}
