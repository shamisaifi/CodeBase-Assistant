from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo = settings.APP_ENV == "development",
    pool_size = 10,
    max_overflow = 20
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
