from fastapi import APIRouter
from app.routes.api.v1 import auth, incident, user, integration
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(incident.router, prefix="/incidents", tags=["incidents"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(integration.router, prefix="/integration", tags=["integrations"])
