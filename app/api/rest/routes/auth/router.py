"""
Authentication router aggregator.

Assembles registration, login, token refresh, and logout sub-routers under the `/auth` prefix.
"""
from fastapi import APIRouter

from app.api.rest.routes.auth.login import router as login_router
from app.api.rest.routes.auth.logout import router as logout_router
from app.api.rest.routes.auth.refresh import router as refresh_router
from app.api.rest.routes.auth.register import router as register_router

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.include_router(register_router)
router.include_router(login_router)
router.include_router(refresh_router)
router.include_router(logout_router)

