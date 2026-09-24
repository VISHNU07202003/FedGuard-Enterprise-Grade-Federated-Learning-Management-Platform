import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_engine
from app.db.models import UserModel
from app.core.security import get_password_hash
from sqlalchemy.future import select

async def seed():
    maker = get_engine()
    async with maker() as db:
        users = [
            {'email': 'admin@fedguard.dev', 'password': 'password123', 'role': 'admin', 'full_name': 'Admin User'},
            {'email': 'researcher@fedguard.dev', 'password': 'password123', 'role': 'researcher', 'full_name': 'Research User'},
            {'email': 'viewer@fedguard.dev', 'password': 'password123', 'role': 'viewer', 'full_name': 'View User'}
        ]
        
        for u in users:
            result = await db.execute(select(UserModel).where(UserModel.email == u['email']))
            if not result.scalars().first():
                user = UserModel(
                    email=u['email'],
                    hashed_password=get_password_hash(u['password']),
                    role=u['role'],
                    full_name=u['full_name']
                )
                db.add(user)
                print(f"Seeded {u['email']}")
            else:
                print(f"User {u['email']} already exists")
        
        await db.commit()

if __name__ == '__main__':
    asyncio.run(seed())