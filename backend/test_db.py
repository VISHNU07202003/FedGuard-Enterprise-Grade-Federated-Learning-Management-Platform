import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
db_url = settings.DATABASE_URL.replace("sslmode=require", "ssl=require")
print(db_url)
engine = create_async_engine(db_url, echo=False)
async def test():
    try:
        async with engine.connect() as conn:
            print("Connected!")
    except Exception as e:
        print(f"Error: {e}")
asyncio.run(test())
