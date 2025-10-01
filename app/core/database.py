from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True)
# echo=True will log all the sql queries to the console

AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()
