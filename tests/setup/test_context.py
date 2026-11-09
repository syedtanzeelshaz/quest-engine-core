import pytest

from app.core.context import (
    get_current_experience,
    reset_current_experience,
    set_current_experience,
)
from app.core.primitives.enums import Experience


def test_experience_context_lifecycle():
    # 1. Uninitialized context should be None
    reset_current_experience()
    assert get_current_experience() is None

    # 2. Set experience
    token = set_current_experience(Experience.OPERATIONS)
    assert get_current_experience() == Experience.OPERATIONS

    # 3. Reset using token restores previous state (None)
    reset_current_experience(token)
    assert get_current_experience() is None

    # 4. Set customer experience
    set_current_experience(Experience.CUSTOMER)
    assert get_current_experience() == Experience.CUSTOMER

    # 5. Reset without token sets to None
    reset_current_experience()
    assert get_current_experience() is None

