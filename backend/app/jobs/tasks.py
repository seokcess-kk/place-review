from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from rq import get_current_job

from app.db.crud import create_analysis, create_review, get_or_create_place
from app.db.session import get_session
from app.models.scrape import ScrapeMode
from app.services import get_analyzer, get_scraper


def update_job_progress(current: int, total: int, stage: str = "processing"):
    job = get_current_job()
    if job:
        job.meta["progress"] = {
            "current": current,
            "total": total,
            "stage": stage,
            "percent": round((current / total) * 100) if total > 0 else 0,
        }
        job.save_meta()


def scrape_and_analyze(
    url: str,
    mode: Optional[str],
    limit_qty: Optional[int],
    limit_date: Optional[date],
) -> Dict[str, Any]:
    update_job_progress(0, 1, "scraping")
    
    scraper = get_scraper()
    analyzer = get_analyzer()
    scrape_mode = ScrapeMode(mode) if mode else ScrapeMode.QTY
    
    items = scraper.scrape(
        url=url,
        mode=scrape_mode,
        limit_qty=limit_qty,
        limit_date=limit_date,
    )
    
    total_items = len(items)
    update_job_progress(0, total_items, "analyzing")
    
    session = get_session()
    try:
        place = get_or_create_place(session, url)
        
        reviews_data: List[Dict[str, Any]] = []
        analyzed_count = 0
        
        for idx, item in enumerate(items):
            review = create_review(
                session=session,
                place=place,
                review_text=item.review,
                review_date=item.date,
            )
            
            try:
                analysis_result = analyzer.analyze(item.review)
                create_analysis(
                    session=session,
                    review=review,
                    sentiment=analysis_result.sentiment.value,
                    keywords=analysis_result.keywords,
                    summary=analysis_result.summary,
                )
                analyzed_count += 1
                
                reviews_data.append({
                    "id": review.id,
                    "text": item.review,
                    "date": item.date.isoformat(),
                    "sentiment": analysis_result.sentiment.value,
                    "keywords": analysis_result.keywords,
                    "summary": analysis_result.summary,
                })
            except Exception:
                reviews_data.append({
                    "id": review.id,
                    "text": item.review,
                    "date": item.date.isoformat(),
                    "sentiment": None,
                    "keywords": [],
                    "summary": None,
                })
            
            update_job_progress(idx + 1, total_items, "analyzing")
        
        session.commit()
        
        return {
            "place_id": place.id,
            "place_url": url,
            "review_count": len(items),
            "analyzed_count": analyzed_count,
            "reviews": reviews_data,
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
