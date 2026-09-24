from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.secrets import config_provider
from app.db.session import get_db
from app.db.models import UserModel
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login" if hasattr(settings, "API_V1_STR") else "/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        from app.core.secrets import get_secret
        jwt_secret = get_secret("JWT_SECRET")
        payload = jwt.decode(token, jwt_secret, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise credentials_exception

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: UserModel = Depends(get_current_active_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user