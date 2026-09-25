"""
Common DataLoader utilities and standardized factory helpers.

Enforces:
- Automatic batching limits (max_batch_size).
- Strict key order preservation.
- Consistent batch execution logging.
"""
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar

from strawberry.dataloader import DataLoader

from app.graphql.common.constants import DEFAULT_LOADER_BATCH_SIZE
from app.util.logger import log

K = TypeVar("K")
T_ORM = TypeVar("T_ORM")
T_GQL = TypeVar("T_GQL")


async def batch_fetch_by_id(
    name: str,
    keys: Sequence[K],
    fetch_fn: Callable[[Sequence[K]], Awaitable[Sequence[T_ORM]]],
    map_fn: Callable[[T_ORM], T_GQL],
    key_extractor: Callable[[T_ORM], K] = lambda entity: getattr(entity, "id"),
) -> list[T_GQL | None]:
    """
    Standardized batch-fetching pipeline:
    1. Logs batch execution.
    2. Invokes repo fetch.
    3. Maps ORM -> GraphQL.
    4. Preserves input key ordering (fills missing records with None).
    """
    log.info("[DataLoader:%s] Batch fetching %d item(s)", name, len(keys))

    entities = await fetch_fn(keys)
    entity_map = {key_extractor(e): map_fn(e) for e in entities}

    return [entity_map.get(k) for k in keys]


def create_dataloader(
    load_fn: Callable[[Sequence[K]], Awaitable[Sequence[T_GQL | None]]],
    max_batch_size: int = DEFAULT_LOADER_BATCH_SIZE,
) -> DataLoader[K, T_GQL | None]:
    """Factory creating request-scoped DataLoader with enforced batch limits."""
    return DataLoader(load_fn=load_fn, max_batch_size=max_batch_size)
