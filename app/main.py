from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import auth, health
from app.core.bootstrap import run_startup_checks
from app.core.database import engine
from app.util.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        run_startup_checks()
    except Exception:
        raise

    yield

    log.info("Disposing database connection engine pool...")
    engine.dispose()
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

    # Infrastructure route (Unversioned for load balancers / k8s probes) -> GET /health
    app.include_router(health.router, prefix="/health")

    # routes
    app.include_router(auth.router, prefix="/api/v1/auth")

    return app


app = create_app()