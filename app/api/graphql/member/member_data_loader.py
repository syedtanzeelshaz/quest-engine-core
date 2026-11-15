"""
Member data loader.
Encapsulates batch-loading operations for the Member domain to eliminate N+1 queries.
"""
from __future__ import annotations

import asyncio

from questengine.registry.types import Member as MemberGraphQL, Role as RoleGraphQL

from app.service.member.factory import build_member_service
from app.util.logger import log


class MemberDataLoader:
    """
    Per-request DataLoader for the Member domain.
    Batches member and child entity lookups per event-loop tick to eliminate N+1 query patterns.
    """

    def __init__(self) -> None:
        self._member_queue: list[tuple[int, asyncio.Future[MemberGraphQL | None]]] = []
        self._member_scheduled = False

        self._roles_queue: list[tuple[int, asyncio.Future[list[RoleGraphQL]]]] = []
        self._roles_scheduled = False


    async def load(self, member_id: int) -> MemberGraphQL | None:
        """Batch-load a Member by ID, eliminating N+1 queries across parent/foreign-key lookups."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[MemberGraphQL | None] = loop.create_future()
        self._member_queue.append((member_id, future))

        if not self._member_scheduled:
            self._member_scheduled = True
            loop.call_soon(self._dispatch_members)

        return await future


    def _dispatch_members(self) -> None:
        queue = self._member_queue
        self._member_queue = []
        self._member_scheduled = False
        if queue:
            asyncio.create_task(self._execute_batch_members(queue))


    async def _execute_batch_members(
        self,
        queue: list[tuple[int, asyncio.Future[MemberGraphQL | None]]],
    ) -> None:
        service = build_member_service()
        member_ids = list({mid for mid, _ in queue})
        log.info("Batch loading members for ids: %s", member_ids)
        try:
            results_by_id = await service.get_members_batch(member_ids)
            for mid, future in queue:
                if not future.done():
                    future.set_result(results_by_id.get(mid))
        except Exception as exc:
            log.error("Failed to batch load members: %s", exc)
            for _, future in queue:
                if not future.done():
                    future.set_exception(exc)


    async def load_roles(self, member_id: int) -> list[RoleGraphQL]:
        """Batch-load assigned roles for a Member, eliminating N+1 queries when resolving member.roles."""
        loop = asyncio.get_running_loop()
        future: asyncio.Future[list[RoleGraphQL]] = loop.create_future()
        self._roles_queue.append((member_id, future))

        if not self._roles_scheduled:
            self._roles_scheduled = True
            loop.call_soon(self._dispatch_roles)

        return await future


    def _dispatch_roles(self) -> None:
        queue = self._roles_queue
        self._roles_queue = []
        self._roles_scheduled = False
        if queue:
            asyncio.create_task(self._execute_batch_roles(queue))


    async def _execute_batch_roles(
        self,
        queue: list[tuple[int, asyncio.Future[list[RoleGraphQL]]]],
    ) -> None:
        service = build_member_service()
        member_ids = list({mid for mid, _ in queue})
        log.info("Batch loading roles for member ids: %s", member_ids)
        try:
            results_by_id = await service.get_roles_for_members_batch(member_ids)
            for mid, future in queue:
                if not future.done():
                    future.set_result(results_by_id.get(mid, []))
        except Exception as exc:
            log.error("Failed to batch load roles: %s", exc)
            for _, future in queue:
                if not future.done():
                    future.set_exception(exc)
