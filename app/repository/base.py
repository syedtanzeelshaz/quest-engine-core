from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class Pageable:
    """Encapsulates pagination and sort parameters for repository queries."""
    page: int = 0
    page_size: int = 20
    sort_by: ColumnElement | None = field(default=None, compare=False)
    sort_order: SortOrder = SortOrder.ASC

    @property
    def offset(self) -> int:
        """Calculated row offset for SQL OFFSET clause."""
        return self.page * self.page_size


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing standard asynchronous CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def find_by_id(self, id: int) -> ModelType | None:
        """Fetch a single record by its primary key ID."""
        return await self.session.get(self.model, id)

    async def find_all(self, pageable: Pageable | None = None) -> list[ModelType]:
        """Fetch records, optionally scoped by a Pageable page window with ordering."""
        stmt = select(self.model)
        if pageable is not None:
            col = pageable.sort_by if pageable.sort_by is not None else self.model.id
            order_expr = col.asc() if pageable.sort_order == SortOrder.ASC else col.desc()
            stmt = stmt.order_by(order_expr).offset(pageable.offset).limit(pageable.page_size)
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_by_ids(self, ids: Sequence[int]) -> list[ModelType]:
        """Fetch all records matching the provided sequence of IDs."""
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def _prefetch_existing(self, objs: Sequence[ModelType]) -> None:
        """Batch-load existing records into the identity map in a single query to eliminate N+1 SELECTs."""
        ids = [
            obj.id
            for obj in objs
            if getattr(obj, "id", None) is not None
        ]
        if ids:
            stmt = select(self.model).where(self.model.id.in_(ids))
            await self.session.scalars(stmt)

    async def save(self, obj: ModelType) -> ModelType:
        """Stage an entity for insert or update without an immediate flush."""
        return await self.session.merge(obj)

    async def save_all(self, objs: Sequence[ModelType]) -> list[ModelType]:
        """Stage multiple entities for insert or update without an immediate flush."""
        if not objs:
            return []
        await self._prefetch_existing(objs)
        return [await self.session.merge(obj) for obj in objs]

    async def save_and_flush(self, obj: ModelType) -> ModelType:
        """Stage an entity for insert or update and immediately flush changes."""
        merged_obj = await self.session.merge(obj)
        await self.session.flush()
        return merged_obj

    async def save_all_and_flush(self, objs: Sequence[ModelType]) -> list[ModelType]:
        """Stage multiple entities for insert or update and immediately flush changes."""
        if not objs:
            return []
        await self._prefetch_existing(objs)
        merged_objs = [await self.session.merge(obj) for obj in objs]
        await self.session.flush()
        return merged_objs

    async def delete(self, obj: ModelType) -> None:
        """Delete a tracked record."""
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, id: int) -> bool:
        """Fetch by ID and delete if found."""
        obj = await self.find_by_id(id)
        if obj is not None:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False

    async def delete_all(self, objs: Sequence[ModelType]) -> None:
        """Delete multiple tracked records."""
        if not objs:
            return
        for obj in objs:
            await self.session.delete(obj)
        await self.session.flush()

    async def delete_all_by_ids(self, ids: Sequence[int]) -> int:
        """Fetch records by IDs and delete them."""
        if not ids:
            return 0
        objs = await self.find_all_by_ids(ids)
        for obj in objs:
            await self.session.delete(obj)
        await self.session.flush()
        return len(objs)


    async def count(self) -> int:
        """Count total rows in the table."""
        stmt = select(func.count()).select_from(self.model)
        return (await self.session.scalar(stmt)) or 0

    async def exists_by_id(self, id: int) -> bool:
        """Check whether a record with the given ID exists."""
        stmt = select(1).select_from(self.model).where(self.model.id == id).limit(1)
        return (await self.session.scalar(stmt)) is not None
