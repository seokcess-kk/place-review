from fastapi import APIRouter, HTTPException

from app.models.scrape import ScrapeRequest, ScrapeResponse
from app.services import get_scraper
from app.services.scraper import ScraperConfigError, ScraperDependencyError

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("", response_model=ScrapeResponse)
async def scrape_reviews(payload: ScrapeRequest) -> ScrapeResponse:
    scraper = get_scraper()
    try:
        items = scraper.scrape(
            url=str(payload.url),
            mode=payload.mode,
            limit_qty=payload.limit_qty,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
    except ScraperConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ScraperDependencyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ScrapeResponse(items=items)
