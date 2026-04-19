"""Authentication routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth import get_password_hash, verify_password, create_access_token, get_current_active_user
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse, UserOut
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
