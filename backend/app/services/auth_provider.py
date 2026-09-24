from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import UserModel
from app.core.security import verify_password
from app.schemas.auth import UserLogin

class AuthProvider(ABC):
    @abstractmethod
    async def authenticate_user(self, db: AsyncSession, creds: UserLogin) -> Optional[UserModel]:
        pass

class LocalJwtAuthProvider(AuthProvider):
    async def authenticate_user(self, db: AsyncSession, creds: UserLogin) -> Optional[UserModel]:
        result = await db.execute(select(UserModel).where(UserModel.email == creds.email))
        user = result.scalars().first()
        if not user:
            return None
        if not verify_password(creds.password, user.hashed_password):
            return None
        return user

class FutureCognitoAuthProvider(AuthProvider):
    async def authenticate_user(self, db: AsyncSession, creds: UserLogin) -> Optional[UserModel]:
        # To be implemented in Phase 13/14 when AWS Bedrock/Cognito are added
        raise NotImplementedError("Cognito auth not implemented yet.")

def get_auth_provider() -> AuthProvider:
    return LocalJwtAuthProvider()