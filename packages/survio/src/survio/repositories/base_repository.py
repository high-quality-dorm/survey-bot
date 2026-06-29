from typing import Generic, Protocol, Sequence, Type, TypeVar

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def create(self, new_object: ModelType, session: AsyncSession) -> None:
        session.add(new_object)


    async def get_all(self, session: AsyncSession) -> Sequence[ModelType]:
        query = select(self.model)
        res = await session.execute(query)
        return res.unique().scalars().all()

    async def get(self, id: int, session: AsyncSession) -> ModelType | None:
        query = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        res = await session.execute(query)
        return res.unique().scalars().one_or_none()

    async def delete(self, id: int, session: AsyncSession) -> None:
        query = delete(self.model).where(self.model.id == id)
        await session.execute(query)
