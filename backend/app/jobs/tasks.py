from __future__ import annotations

from typing import Dict, Optional

from app.models.scrape import ScrapeMode
from app.services import get_analyzer, get_scraper


def scrape_and_analyze(url: str, mode: Optional[str], limit_qty: Optional[int]) -> Dict[str, int]:
    scraper = get_scraper()
    analyzer = get_analyzer()
    scrape_mode = ScrapeMode(mode) if mode else ScrapeMode.QTY
    items = scraper.scrape(
        url=url,
        mode=scrape_mode,
        limit_qty=limit_qty or 1,
        limit_date=None,
    )
    for item in items:
        analyzer.analyze(item.review)
    return {"review_count": len(items)}
