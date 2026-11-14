"""
GraphQL per-request context builder.
Resolves caller identity from Bearer token into the canonical CurrentUser principal.
"""
from __future__ import annotations

import logging
from starlette.requests import Request

from app.graphql.context import GraphQLContext
from app.service.user.factory import build_current_user_service

logger = logging.getLogger(__name__)


async def build_graphql_context(request: Request) -> GraphQLContext:
    """
    Construct GraphQLContext for each incoming GraphQL query or mutation.
    Extracts Bearer token and verifies principal into CurrentUser (with permissions pre-loaded).
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return GraphQLContext(request=request)

    token = auth_header[7:].strip()
    if not token:
        return GraphQLContext(request=request)

    user_service = build_current_user_service()
    try:
        current_user = await user_service.get_user_from_token(token)
        if current_user is None or not current_user.is_active:
            return GraphQLContext(request=request)
        return GraphQLContext(request=request, caller=current_user)
    except Exception as exc:
        logger.debug("Failed to resolve current user from token: %s", exc)
        return GraphQLContext(request=request)
