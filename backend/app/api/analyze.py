from fastapi import APIRouter, HTTPException

from app.models.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import (
    AnalyzerConfigError,
    AnalyzerDependencyError,
    get_analyzer,
)

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_review(payload: AnalyzeRequest) -> AnalyzeResponse:
    analyzer = get_analyzer()
    try:
        return analyzer.analyze(payload.review)
    except AnalyzerConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AnalyzerDependencyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
