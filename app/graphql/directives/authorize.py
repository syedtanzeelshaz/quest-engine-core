"""
Authorize directive execution handler.
Evaluates caller permissions and experience context against @authorize directive annotations.
"""
from __future__ import annotations

import inspect
from typing import Any

from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLField, GraphQLResolveInfo, default_field_resolver
from graphql.error import GraphQLError

from app.core.primitives.enums import Experience
from app.graphql.context import GraphQLContext


class AuthorizeDirective(SchemaDirectiveVisitor):
    """
    Schema directive visitor for @authorize(customer: [...], operations: [...]).
    Validates caller authentication and checks assigned permissions for active experience.
    """

    def visit_object(self, object_type: Any) -> Any:
        return object_type

    def visit_input_field_definition(self, field: Any, object_type: Any) -> Any:
        return field

    def visit_field_definition(self, field: GraphQLField, object_type: Any) -> GraphQLField:
        original_resolver = field.resolve or default_field_resolver

        customer_perms: list[str] = self.args.get("customer") or []
        operations_perms: list[str] = self.args.get("operations") or []

        async def resolve_authorized(obj: Any, info: GraphQLResolveInfo, **kwargs: Any) -> Any:
            context: GraphQLContext | None = getattr(info, "context", None)
            if not isinstance(context, GraphQLContext) or not context.is_authenticated or context.caller is None:
                raise GraphQLError(
                    "Authentication required to access this resource.",
                    extensions={"code": "UNAUTHORIZED", "status": 401},
                )

            # Determine required permissions based on active experience
            if context.experience == Experience.OPERATIONS:
                required = operations_perms
            else:
                required = customer_perms

            # If directive specifies restrictions for this experience, evaluate against caller permissions
            if required:
                if not context.caller.has_any_permission(required):
                    raise GraphQLError(
                        f"Access denied: Missing required permission for {context.experience.value} context.",
                        extensions={
                            "code": "FORBIDDEN",
                            "status": 403,
                            "required": required,
                        },
                    )

            # Execute underlying resolver
            if inspect.iscoroutinefunction(original_resolver):
                return await original_resolver(obj, info, **kwargs)
            res = original_resolver(obj, info, **kwargs)
            if inspect.isawaitable(res):
                return await res
            return res

        field.resolve = resolve_authorized
        return field
