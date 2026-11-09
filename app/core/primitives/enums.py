"""
Core shared domain enumerations.
"""
from enum import StrEnum


class Experience(StrEnum):
    """
    Platform operational contexts / target user experiences.

    - CUSTOMER: External customer-facing workspace and personal accounts (Member persona).
    - OPERATIONS: Internal platform operations, admin, and support portal (Operator persona).
    """

    CUSTOMER = "CUSTOMER"
    OPERATIONS = "OPERATIONS"
