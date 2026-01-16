from fastapi import APIRouter
from pydantic import BaseModel

from app.core.settings import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    return HealthResponse(status="ok", environment=settings.app_env)
