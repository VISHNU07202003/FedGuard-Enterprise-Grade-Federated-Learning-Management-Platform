"""FedGuard — Privacy-Preserving Federated Anomaly Detection Platform."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import FedGuardError, fedguard_exception_handler
from app.api.routes.health import router as health_router

from app.db.session import close_db_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    from app.core.secrets import config_provider, get_secret
    from urllib.parse import urlparse
    
    # 4. Fail fast if DATABASE_URL cannot be loaded
    db_url = get_secret("DATABASE_URL")
    parsed = urlparse(db_url)
    
    # 5. Add startup logging showing which configuration provider was selected
    logger.info(
        "FedGuard API starting",
        extra={
            "environment": settings.ENVIRONMENT,
            "db_host": parsed.hostname,
            "config_provider": config_provider.name
        },
    )
    logger.info(f"Configuration Provider loaded: {config_provider.name}")
    logger.info(f"Connected to database host: {parsed.hostname}")
    yield
    logger.info("FedGuard API shutting down")
    await close_db_connection()
    logger.info("Database connection pool disposed")


app = FastAPI(
    title="FedGuard API",
    description="Privacy-Preserving Federated Anomaly Detection Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://frontend:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(FedGuardError, fedguard_exception_handler)

from app.api.router import api_router
from app.api.websocket import router as websocket_router
from app.observability.middleware import PrometheusMiddleware
from prometheus_client import make_asgi_app

# Add Prometheus Middleware
app.add_middleware(PrometheusMiddleware)

# Mount Prometheus metrics endpoint (ASGI app)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health endpoints at root level (not under /api/v1)
app.include_router(health_router)

# Include v1 API router
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket router
app.include_router(websocket_router)
