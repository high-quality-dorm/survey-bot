import pytest
from survio.db.models import Users

@pytest.mark.asyncio
async def test_user_repo_create(session, user_repo):
    user = Users(id=123)
    await user_repo.create(user, session)
    await session.commit()
    result = await user_repo.get(123, session)
    assert result is not None
    assert result.id == 123

@pytest.mark.asyncio
async def test_user_repo_get_all(session, user_repo):
    user1 = Users(id=1)
    user2 = Users(id=2)
    session.add_all([user1, user2])
    await session.commit()
    users = await user_repo.get_all(session)
    assert len(users) == 2
    ids = [u.id for u in users]
    assert 1 in ids and 2 in ids

@pytest.mark.asyncio
async def test_user_repo_delete(session, user_repo):
    user = Users(id=5)
    session.add(user)
    await session.commit()
    await user_repo.delete(5, session)
    await session.commit()
    result = await user_repo.get(5, session)
    assert result is None