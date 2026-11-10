"""
User registration route handler.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_experience_context
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_registration_service
from app.api.rest.routes.auth.helpers import make_token_response
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import EmailAlreadyExistsError
from app.schema.authentication.auth import RegisterRequest, RegisterResponse
from app.service.authentication.models import RegisterCommand
from app.service.authentication.registration_service import RegistrationService
from app.util.logger import log

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=HttpCode._201)
async def register(
    body: RegisterRequest,
    experience: Experience = Depends(get_experience_context),
    registration_service: RegistrationService = Depends(get_registration_service),
) -> RegisterResponse:
    """Register a new user account and return JWT tokens."""
    log.info("Received registration request for email: %s, experience: %s", body.email, experience)

    try:
        user, persona, token_pair = await registration_service.register(
            RegisterCommand(
                email=body.email,
                plain_password=body.password.get_secret_value(),
                first_name=body.first_name,
                last_name=body.last_name,
                experience=experience,
            )
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=HttpCode._409,
            detail=HttpMessage.EMAIL_ALREADY_REGISTERED,
        )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        first_name=persona.first_name,
        last_name=persona.last_name,
        experience=user.experience,
        tokens=make_token_response(token_pair),
    )

