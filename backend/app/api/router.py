from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.training import router as training_router
from app.api.routes.clients import router as clients_router
from app.api.routes.experiments import router as experiments_router
from app.api.routes.models import router as models_router
from app.api.routes.security import router as security_router
from app.api.routes.audit import router as audit_router
from app.api.routes.auth import router as auth_router
from app.api.routes.copilot import router as copilot_router

api_router = APIRouter()

# Auth router manages its own dependencies (login must be public)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# All other API routes require an active user session
secure_depends = [Depends(get_current_active_user)]
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"], dependencies=secure_depends)
api_router.include_router(training_router, prefix="/training", tags=["training"], dependencies=secure_depends)
api_router.include_router(clients_router, prefix="/clients", tags=["clients"], dependencies=secure_depends)
api_router.include_router(experiments_router, prefix="/experiments", tags=["experiments"], dependencies=secure_depends)
api_router.include_router(models_router, prefix="/models", tags=["models"], dependencies=secure_depends)
api_router.include_router(security_router, prefix="/security", tags=["security"], dependencies=secure_depends)
api_router.include_router(audit_router, prefix="/audit", tags=["audit"], dependencies=secure_depends)
api_router.include_router(copilot_router, prefix="/copilot", tags=["copilot"], dependencies=secure_depends)

