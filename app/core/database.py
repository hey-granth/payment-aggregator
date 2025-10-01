from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,     # pool_pre_ping to check if connection is alive
    connect_args={"ssl": "require"}     # we usually add ssl required in db url only, but asyncpg works in a bit different way
)

AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()
