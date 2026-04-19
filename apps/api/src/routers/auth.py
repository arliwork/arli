"""Authentication routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth import get_password_hash, verify_password, create_access_token, get_current_active_user
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse, UserOut, LLMConfigUpdate, LLMConfigOut
from dependencies import get_async_db

router = APIRouter(prefix="/auth", tags=["auth"])

def _set_cookie(response: JSONResponse, token: str) -> JSONResponse:
    response.set_cookie(
        key="arli_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=604800,
    )
    return response

@router.post("/register", summary="Register new user", response_description="User created with JWT token")
async def register(data: UserRegister, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token(data={"sub": str(user.id)})
    payload = TokenResponse(access_token=token, user=UserOut.model_validate(user)).model_dump(mode="json")
    resp = JSONResponse(content=payload)
    return _set_cookie(resp, token)

@router.post("/login", summary="User login", response_description="JWT token in cookie + response body")
async def login(data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id)})
    payload = TokenResponse(access_token=token, user=UserOut.model_validate(user)).model_dump(mode="json")
    resp = JSONResponse(content=payload)
    return _set_cookie(resp, token)

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_active_user)):
    return UserOut.model_validate(current_user)

@router.post("/principal", response_model=UserOut)
async def update_principal(
    principal: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Link ICP principal to user account"""
    current_user.principal = principal
    await db.commit()
    await db.refresh(current_user)
    return UserOut.model_validate(current_user)

@router.get("/wallet/balance")
async def wallet_balance(principal: str):
    """Get ICP balance for a principal (calls ICP ledger via icp_integration)"""
    try:
        from icp_integration import icp_client
        balance_e8s = await icp_client.check_balance(principal)
        return {"balance_icp": balance_e8s / 100_000_000, "balance_e8s": balance_e8s}
    except Exception as e:
        # If ICP client is not configured, return 0 with a note
        return {"balance_icp": 0, "balance_e8s": 0, "note": str(e)}

@router.get("/me/llm-config", response_model=LLMConfigOut)
async def get_llm_config(current_user: User = Depends(get_current_active_user)):
    """Get current user's LLM provider configuration (api_key is NOT returned for security)"""
    return LLMConfigOut(
        provider=current_user.llm_provider or "kimi",
        model=current_user.llm_model,
        base_url=current_user.llm_base_url,
    )

@router.post("/me/llm-config", response_model=UserOut)
async def update_llm_config(
    data: LLMConfigUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's LLM provider configuration"""
    current_user.llm_provider = data.provider
    current_user.llm_api_key = data.api_key
    current_user.llm_base_url = data.base_url or None
    current_user.llm_model = data.model or None
    await db.commit()
    await db.refresh(current_user)
    return UserOut.model_validate(current_user)

@router.delete("/me/llm-config")
async def delete_llm_config(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Clear user's LLM config (fallback to system defaults)"""
    current_user.llm_provider = None
    current_user.llm_api_key = None
    current_user.llm_base_url = None
    current_user.llm_model = None
    await db.commit()
    await db.refresh(current_user)
    return {"success": True, "message": "LLM config cleared"}
