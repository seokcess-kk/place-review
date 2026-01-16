from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.core.settings import get_settings


class ErrorResponse(BaseModel):
    detail: str


app = FastAPI(title="Place Review API")


@app.exception_handler(ValueError)
async def value_error_handler(_, exc: ValueError):
    return JSONResponse(status_code=400, content=ErrorResponse(detail=str(exc)).model_dump())


@app.on_event("startup")
async def load_settings():
    get_settings()


app.include_router(health_router)
app.include_router(jobs_router)
