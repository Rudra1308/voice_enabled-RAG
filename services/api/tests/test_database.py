import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.repositories import user_repo

# We will test against the local db since docker is running. 
# Normally you'd use a test DB.
TEST_DATABASE_URL = "postgresql+asyncpg://voicerag:voicerag_secret@localhost:5432/voicerag_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

import pytest_asyncio


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    # Test DB insertion
    user = await user_repo.create(db_session, obj_in={"email": "test@example.com"})
    assert user.id is not None
    assert user.email == "test@example.com"
    
    # Clean up
    await user_repo.remove(db_session, id=user.id)
