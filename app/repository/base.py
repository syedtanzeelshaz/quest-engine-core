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

    def create(self, obj: ModelType) -> ModelType:
        """Add and flush a new record."""
        self.session.add(obj)
        self.session.flush()
        return obj

    def create_all(self, objs: Sequence[ModelType]) -> list[ModelType]:
        """Add and flush multiple new records."""
        if not objs:
            return []
        self.session.add_all(objs)
        self.session.flush()
        return list(objs)

    def update(self, obj: ModelType) -> ModelType:
        """Flush modifications on an existing tracked record."""
        self.session.flush()
        return obj

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

    def count(self) -> int:
        """Count total rows in the table."""
        stmt = select(func.count()).select_from(self.model)
        return self.session.scalar(stmt) or 0

    def exists_by_id(self, id: int) -> bool:
        """Check whether a record with the given ID exists."""
        stmt = select(1).select_from(self.model).where(self.model.id == id).limit(1)
        return self.session.scalar(stmt) is not None
