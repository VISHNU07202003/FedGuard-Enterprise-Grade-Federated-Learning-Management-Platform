from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.secrets import get_secret

_engine = None
_sessionmaker = None

def get_engine():
    global _engine, _sessionmaker
    if _engine is None:
        db_url = get_secret("DATABASE_URL")
        _engine = create_async_engine(db_url, echo=False)
        _sessionmaker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    return _sessionmaker

async def get_db():
    maker = get_engine()
    async with maker() as session:
        yield session

async def close_db_connection():
    global _engine
    if _engine is not None:
        await _engine.dispose()
