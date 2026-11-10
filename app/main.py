from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.model
from app import __version__
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.routes import auth, health
from app.core.bootstrap import run_startup_checks
from app.core.database import DatabaseSessionMiddleware, engine
from app.util.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_startup_checks()
    yield

    log.info("Disposing database connection engine pool...")
    await engine.dispose()
    log.info("Shutting down Quest Engine Core application...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Quest Engine Core Service",
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Automatically manages request-scoped database session and transaction lifecycle
    app.add_middleware(DatabaseSessionMiddleware)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Sanitize 422 validation errors by stripping the raw 'input' field.
        Prevents sensitive user input (such as passwords and credentials)
        from leaking into error response bodies, client logs, or APM tools.
        """
        sanitized_errors = []
        for error in exc.errors():
            err = dict(error)
            err.pop("input", None)
            sanitized_errors.append(err)

        return JSONResponse(
            status_code=HttpCode._422,
            content={"detail": jsonable_encoder(sanitized_errors)},
        )

    # Infrastructure route (Unversioned for load balancers / k8s probes) -> GET /health
    app.include_router(health.router, prefix="/health")

    # REST API routes
    app.include_router(auth.router, prefix="/api/v1")

    return app


app = create_app()