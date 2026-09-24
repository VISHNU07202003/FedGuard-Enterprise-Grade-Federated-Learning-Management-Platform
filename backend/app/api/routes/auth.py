from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.db.session import get_db
from app.core.security import create_access_token
from app.db.models import UserModel
from app.schemas.auth import Token, UserOut, UserLogin
from app.api.deps import get_current_active_user
from app.services.auth_provider import get_auth_provider

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    auth_provider = get_auth_provider()
    # OAuth2PasswordRequestForm expects username and password
    creds = UserLogin(email=form_data.username, password=form_data.password)
    user = await auth_provider.authenticate_user(db, creds)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    from app.services.audit_service import log_audit_event
    await log_audit_event(db, actor=user.email, action="login", resource_type="user", resource_id=user.id)
    
    return {
        "access_token": create_access_token({"sub": user.id, "role": user.role}),
        "token_type": "bearer",
    }

@router.post("/logout")
async def logout(current_user: UserModel = Depends(get_current_active_user)) -> Any:
    """
    Log out. For JWT, this is handled on the client side by dropping the token.
    Could implement a blacklist here if needed.
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user