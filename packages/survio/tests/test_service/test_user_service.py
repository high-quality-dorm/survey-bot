import pytest
from survio.services.user_service import UserService

@pytest.mark.asyncio
async def test_user_service_get_existing(session):
    service = UserService()
    from survio.repositories.user_repository import UserRepository
    from survio.db.models import Users
    repo = UserRepository(Users)
    user = Users(id=123)
    await repo.create(user, session)
    await session.flush()
    result = await service.get(123, session)
    assert result is not None
    assert result.id == 123

@pytest.mark.asyncio
async def test_user_service_get_not_found(session):
    service = UserService()
    result = await service.get(999, session)
    assert result is None

@pytest.mark.asyncio
async def test_user_service_create(session):
    service = UserService()
    user = await service.create(456, session)
    assert user.id == 456
    from survio.repositories.user_repository import UserRepository
    from survio.db.models import Users
    repo = UserRepository(Users)
    saved = await repo.get(456, session)
    assert saved is not None

@pytest.mark.asyncio
async def test_user_service_get_all(session):
    service = UserService()
    from survio.repositories.user_repository import UserRepository
    from survio.db.models import Users
    repo = UserRepository(Users)
    await repo.create(Users(id=1), session)
    await repo.create(Users(id=2), session)
    await session.flush()
    users = await service.get_all(session)
    assert len(users) >= 2
    ids = [u.id for u in users]
    assert 1 in ids and 2 in ids