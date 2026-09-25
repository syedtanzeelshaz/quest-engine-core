"""User domain validator."""
import re
from datetime import date

from app.core.exceptions import InvalidInputError
from app.graphql.user.inputs import UpdateUserProfileInput
from app.util.logger import log

# Allows optional leading '+', digits, spaces, hyphens, and parentheses (between 7 and 25 characters)
PHONE_FORMAT_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,25}$")


class UserValidator:
    """Validates user domain business rules and profile input constraints."""

    def __init__(self) -> None:
        pass


    def validate_user_update_inputs(self, input_data: UpdateUserProfileInput) -> None:
        """Validate all mutable fields in UpdateUserProfileInput."""
        if input_data.phone is not None:
            self.validate_phone(input_data.phone)

        if input_data.date_of_birth is not None:
            self.validate_date_of_birth(input_data.date_of_birth)

        if input_data.first_name is not None:
            self.validate_name("first_name", input_data.first_name)

        if input_data.last_name is not None:
            self.validate_name("last_name", input_data.last_name)


    def validate_phone(self, phone: str) -> None:
        """
        Validate phone number:
        - Must not contain any alphabetic characters.
        - Must follow standard phone format: optional leading '+', digits, hyphens, spaces, and parentheses.
        """
        phone_stripped = phone.strip()

        if any(c.isalpha() for c in phone_stripped):
            log.warning("[validate_phone] Phone number contains alphabetic characters: %s", phone)
            raise InvalidInputError("Phone number cannot contain alphabetic characters.")

        if not PHONE_FORMAT_REGEX.match(phone_stripped):
            log.warning("[validate_phone] Invalid phone number format: %s", phone)
            raise InvalidInputError("Invalid phone number format.")


    def validate_date_of_birth(self, dob: date) -> None:
        """
        Validate date of birth:
        - Must be on or after 1900-01-01.
        - Cannot be in the future.
        """
        min_dob = date(1900, 1, 1)
        today = date.today()

        if dob < min_dob:
            log.warning("[validate_date_of_birth] Date of birth %s is earlier than %s", dob, min_dob)
            raise InvalidInputError("Date of birth cannot be before 1900-01-01.")

        if dob > today:
            log.warning("[validate_date_of_birth] Date of birth %s is in the future", dob)
            raise InvalidInputError("Date of birth cannot be in the future.")


    def validate_name(self, field_name: str, name: str) -> None:
        """Validate names are not blank or only whitespace when provided."""
        if not name.strip():
            log.warning("[validate_name] %s is empty or only whitespace", field_name)
            raise InvalidInputError(f"{field_name.replace('_', ' ').capitalize()} cannot be empty or whitespace.")
