from fastapi import APIRouter

from app.util.logger import log

router = APIRouter(tags=["Authentication"])


@router.post("/register", summary="Register a new user")
def register_user():
    log.info("Received request for user registration.")
    return {"message": "User registration endpoint placeholder"}


@router.post("/login", summary="Authenticate user & issue JWT")
def login_user():
    log.info("Received request for user login.")
    return {"message": "User login endpoint placeholder"}
