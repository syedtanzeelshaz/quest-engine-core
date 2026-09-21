from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing standard CRUD operations."""

    def __init__(self, model: type[ModelType], session: Session) -> None:
        self.model = model
        self.session = session

    def find_by_id(self, id: int) -> ModelType | None:
        """Fetch a single record by its primary key ID."""
        return self.session.get(self.model, id)

    def find_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Fetch records with pagination support."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def find_all_by_ids(self, ids: Sequence[int]) -> list[ModelType]:
        """Fetch all records matching the provided sequence of IDs."""
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))
        return list(self.session.scalars(stmt).all())

    def _prefetch_existing(self, objs: Sequence[ModelType]) -> None:
        """Batch-load existing records into the identity map in a single query to eliminate N+1 SELECTs."""
        ids = [
            getattr(obj, "id")
            for obj in objs
            if getattr(obj, "id", None) is not None
        ]
        if ids:
            stmt = select(self.model).where(self.model.id.in_(ids))
            self.session.scalars(stmt).all()

    def save(self, obj: ModelType) -> ModelType:
        """Stage an entity for insert or update without an immediate flush."""
        return self.session.merge(obj)

    def save_all(self, objs: Sequence[ModelType]) -> list[ModelType]:
        """Stage multiple entities for insert or update without an immediate flush."""
        if not objs:
            return []
        self._prefetch_existing(objs)
        return [self.session.merge(obj) for obj in objs]

    def save_and_flush(self, obj: ModelType) -> ModelType:
        """Stage an entity for insert or update and immediately flush changes."""
        merged_obj = self.session.merge(obj)
        self.session.flush()
        return merged_obj

    def save_all_and_flush(self, objs: Sequence[ModelType]) -> list[ModelType]:
        """Stage multiple entities for insert or update and immediately flush changes."""
        if not objs:
            return []
        self._prefetch_existing(objs)
        merged_objs = [self.session.merge(obj) for obj in objs]
        self.session.flush()
        return merged_objs

    def delete(self, obj: ModelType) -> None:
        """Delete a tracked record."""
        self.session.delete(obj)
        self.session.flush()

    def delete_by_id(self, id: int) -> bool:
        """Fetch by ID and delete if found."""
        obj = self.find_by_id(id)
        if obj is not None:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def delete_all(self, objs: Sequence[ModelType]) -> None:
        """Delete multiple tracked records."""
        if not objs:
            return
        for obj in objs:
            self.session.delete(obj)
        self.session.flush()

    def delete_all_by_ids(self, ids: Sequence[int]) -> int:
        """Fetch records by IDs and delete them."""
        if not ids:
            return 0
        objs = self.find_all_by_ids(ids)
        for obj in objs:
            self.session.delete(obj)
        self.session.flush()
        return len(objs)

    def count(self) -> int:
        """Count total rows in the table."""
        stmt = select(func.count()).select_from(self.model)
        return self.session.scalar(stmt) or 0

    def exists_by_id(self, id: int) -> bool:
        """Check whether a record with the given ID exists."""
        stmt = select(1).select_from(self.model).where(self.model.id == id).limit(1)
        return self.session.scalar(stmt) is not None
