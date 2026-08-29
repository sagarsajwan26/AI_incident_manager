from fastapi import APIRouter
from app.routes.api.v1 import auth, incident

from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(incident.router, prefix="/incidents", tags=["incidents"])
