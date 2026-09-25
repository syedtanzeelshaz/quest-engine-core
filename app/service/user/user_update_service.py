"""User update domain service."""
from app.core.primitives.constants import UserMessage
from app.core.primitives.exceptions import UserNotFoundError
from app.core.transaction import transactional
from app.graphql.user.inputs import UpdateUserProfileInput
from app.model.identity.app_user import AppUser
from app.repository.identity.app_user_repo import AppUserRepository
from app.service.user.user_validator import UserValidator
from app.util.logger import log


class UserUpdateService:
    """Domain service handling user profile and attribute updates."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        user_validator: UserValidator,
    ) -> None:
        self._user_repo = user_repo
        self._user_validator = user_validator


    @transactional
    async def update(
        self,
        user_id: int,
        input_data: UpdateUserProfileInput,
    ) -> AppUser:
        """
        Update mutable profile attributes for a user.

        Raises:
            UserNotFoundError: If no user with the given ID exists.
            InvalidInputError: If any profile field fails domain validation.
        """
        log.info("[update] Updating user profile for user_id=%s, with input=%s", user_id, input_data)

        self._user_validator.validate_user_update_inputs(input_data)

        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            log.warning("[update] User with user_id=%s not found", user_id)
            raise UserNotFoundError(UserMessage.USER_NOT_FOUND)

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
        log.info("[update] Updated user profile for user_id=%s successfully", user_id)

        return updated_user
