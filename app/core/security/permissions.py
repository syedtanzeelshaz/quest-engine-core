"""
Permission matching and authorization evaluation rules.
Provides hierarchical wildcard evaluation (*.customer.**, *.operations.**) and exact matching.
"""
from __future__ import annotations

from collections.abc import Iterable


def matches_permission(caller_perm: str, required_perm: str) -> bool:
    """
    Check if a single caller permission satisfies a required permission string.

    Supports:
      - Exact matching: 'view.customer.member' == 'view.customer.member'
      - Single-segment wildcard (*): '*.customer.member' matches 'view.customer.member'
      - Multi-segment tail wildcard (**): '*.customer.**' matches 'view.customer.organization.role'
    """
    if caller_perm == required_perm:
        return True

    caller_parts = caller_perm.split(".")
    req_parts = required_perm.split(".")

    i = 0
    j = 0
    while i < len(caller_parts) and j < len(req_parts):
        part = caller_parts[i]
        if part == "**":
            return True
        elif part == "*" or part == req_parts[j]:
            i += 1
            j += 1
        else:
            return False

    if i < len(caller_parts) and caller_parts[i] == "**":
        return True

    return i == len(caller_parts) and j == len(req_parts)


def has_matching_permission(caller_permissions: Iterable[str], required_permission: str) -> bool:
    """Check if the caller's assigned permissions satisfy a specific required permission."""
    return any(matches_permission(caller_perm, required_permission) for caller_perm in caller_permissions)


def has_any_permission(caller_permissions: Iterable[str], required_permissions: Iterable[str]) -> bool:
    """Check if the caller's assigned permissions satisfy any of the required permissions."""
    return any(has_matching_permission(caller_permissions, req) for req in required_permissions)
