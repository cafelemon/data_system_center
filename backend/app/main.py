from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.archives import router as archives_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.settings import router as settings_router
from app.api.statistics import router as statistics_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(archives_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(settings_router, prefix=settings.api_prefix)
    app.include_router(statistics_router, prefix=settings.api_prefix)
    app.include_router(users_router, prefix=settings.api_prefix)

    return app


app = create_app()
