from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from importlib.util import find_spec
import re
from typing import Iterable, List, Optional, Protocol

from app.models.scrape import ReviewItem, ScrapeMode


class ScraperConfigError(ValueError):
    pass


class ScraperDependencyError(RuntimeError):
    pass


class Scraper(Protocol):
    def scrape(
        self,
        url: str,
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> List[ReviewItem]:
        ...


@dataclass
class PlaywrightScraper:
    max_scrolls: int = 12
    scroll_pause: float = 1.25

    def scrape(
        self,
        url: str,
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> List[ReviewItem]:
        if find_spec("playwright") is None:
            raise ScraperDependencyError(
                "Playwright is missing; install playwright and run playwright install chromium"
            )
        if find_spec("bs4") is None:
            raise ScraperDependencyError("BeautifulSoup is missing; install beautifulsoup4")

        if mode == ScrapeMode.QTY and limit_qty is None:
            raise ScraperConfigError("limit_qty is required when mode is QTY")
        if mode == ScrapeMode.DATE and limit_date is None:
            raise ScraperConfigError("limit_date is required when mode is DATE")

        from bs4 import BeautifulSoup
        from playwright.sync_api import sync_playwright
        import time
        import shutil

        chromium_path = shutil.which("chromium")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=chromium_path,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(str(url), wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)

                seen_keys: set[tuple[date, str]] = set()
                collected: List[ReviewItem] = []
                stable_count = 0
                previous_count = 0

                for _ in range(self.max_scrolls):
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    parsed_items = self._parse_items(soup.select("li.place_apply_pui"))

                    for item in parsed_items:
                        key = (item.date, item.review)
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)
                        collected.append(item)

                    if self._should_stop(collected, mode, limit_qty, limit_date):
                        break

                    if len(collected) == previous_count:
                        stable_count += 1
                    else:
                        stable_count = 0

                    if stable_count >= 2:
                        break

                    previous_count = len(collected)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(self.scroll_pause)
                    self._click_more(page)

                return self._filter_items(collected, mode, limit_qty, limit_date)
            finally:
                context.close()
                browser.close()

    @staticmethod
    def _parse_items(raw_items: Iterable) -> List[ReviewItem]:
        items: List[ReviewItem] = []
        for item in raw_items:
            text = PlaywrightScraper._extract_review_text(item)
            if not text:
                continue
            review_date = PlaywrightScraper._extract_review_date(item)
            items.append(ReviewItem(date=review_date, review=text))
        return items

    @staticmethod
    def _extract_review_text(item) -> Optional[str]:
        text_area = item.select_one("div.pui__vn15t2 a")
        if not text_area:
            return None
        text = text_area.get_text(strip=True)
        if text.endswith("더보기"):
            text = text[:-3]
        return text or None

    @staticmethod
    def _extract_review_date(item) -> date:
        for span in item.select(".pui__gfuUIT .pui__blind"):
            if "년" not in span.text:
                continue
            parsed = PlaywrightScraper._parse_korean_date(span.text)
            if parsed:
                return parsed
        return date.today()

    @staticmethod
    def _parse_korean_date(text: str) -> Optional[date]:
        match = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text)
        if not match:
            return None
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None

    def _should_stop(
        self,
        items: List[ReviewItem],
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> bool:
        if mode == ScrapeMode.QTY and limit_qty is not None:
            return len(items) >= limit_qty
        if mode == ScrapeMode.DATE and limit_date is not None:
            oldest = min((item.date for item in items), default=date.today())
            return oldest < limit_date
        return False

    def _filter_items(
        self,
        items: List[ReviewItem],
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> List[ReviewItem]:
        if mode == ScrapeMode.QTY and limit_qty is not None:
            return items[:limit_qty]
        if mode == ScrapeMode.DATE and limit_date is not None:
            return [item for item in items if item.date >= limit_date]
        return items

    @staticmethod
    def _click_more(page) -> None:
        try:
            more_button = page.query_selector("a.fvwqf")
            if more_button:
                more_button.click()
                page.wait_for_timeout(500)
        except Exception:
            pass


def get_scraper() -> Scraper:
    return PlaywrightScraper()
