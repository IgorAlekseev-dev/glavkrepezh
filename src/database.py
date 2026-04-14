from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_session():
    async with async_session_maker() as session:
        yield session
    
class Base(DeclarativeBase):
    pass