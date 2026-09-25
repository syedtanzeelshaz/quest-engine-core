"""User domain service."""
from app.core.exceptions import UserNotFoundError
from app.core.transaction import transactional
from app.graphql.user.inputs import UpdateUserProfileInput
from app.model.identity.app_user import AppUser
from app.repository.identity.app_user_repo import AppUserRepository
from app.util.logger import log


class UserService:
    """Core domain service for user profile operations."""

    def __init__(self, user_repo: AppUserRepository) -> None:
        self._user_repo = user_repo

    async def get_user_by_id(self, user_id: int) -> AppUser | None:
        """Fetch an application user by their primary key ID."""
        return await self._user_repo.find_by_id(user_id)

    @transactional
    async def update_profile(
        self,
        user_id: int,
        input_data: UpdateUserProfileInput,
    ) -> AppUser:
        """
        Update mutable profile attributes for a user.

        Raises:
            UserNotFoundError: If no user with the given ID exists.
        """
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found.")

        log.info("[update_profile] Updating user profile for user_id=%s, with input=%s", user_id, input_data)

        if input_data.first_name is not None:
            user.first_name = input_data.first_name
        if input_data.last_name is not None:
            user.last_name = input_data.last_name
        if input_data.phone is not None:
            user.phone = input_data.phone
        if input_data.country is not None:
            user.country = input_data.country
        if input_data.gender is not None:
            user.gender = input_data.gender
        if input_data.date_of_birth is not None:
            user.date_of_birth = input_data.date_of_birth

        updated_user = await self._user_repo.save_and_flush(user)
        log.info("[update_profile] Updated user profile for user_id=%s successfully", user_id)

        return updated_user
