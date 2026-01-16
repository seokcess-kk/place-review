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
        start_date: Optional[date],
        end_date: Optional[date] = None,
    ) -> List[ReviewItem]:
        ...


@dataclass
class PlaywrightScraper:
    max_scrolls: int = 20
    scroll_pause: float = 1.5

    def scrape(
        self,
        url: str,
        mode: ScrapeMode,
        limit_qty: Optional[int],
        start_date: Optional[date],
        end_date: Optional[date] = None,
    ) -> List[ReviewItem]:
        if find_spec("playwright") is None:
            raise ScraperDependencyError(
                "Playwright is missing; install playwright and run playwright install chromium"
            )
        if find_spec("bs4") is None:
            raise ScraperDependencyError("BeautifulSoup is missing; install beautifulsoup4")

        if mode == ScrapeMode.QTY and limit_qty is None:
            raise ScraperConfigError("limit_qty is required when mode is QTY")
        if mode == ScrapeMode.DATE and start_date is None:
            raise ScraperConfigError("start_date is required when mode is DATE")
        if mode == ScrapeMode.DATE_RANGE and (start_date is None or end_date is None):
            raise ScraperConfigError("start_date and end_date are required when mode is DATE_RANGE")

        from bs4 import BeautifulSoup
        from playwright.sync_api import sync_playwright
        import time
        import shutil

        chromium_path = shutil.which("chromium")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=chromium_path,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                viewport={"width": 412, "height": 915}
            )
            page = context.new_page()

            try:
                review_url = self._get_review_url(str(url))
                page.goto(review_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                seen_keys: set[tuple[date, str]] = set()
                collected: List[ReviewItem] = []
                stable_count = 0
                previous_count = 0

                for scroll_idx in range(self.max_scrolls):
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")

                    parsed_items = self._parse_items(soup)

                    for item in parsed_items:
                        key = (item.date, item.review[:50] if len(item.review) > 50 else item.review)
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)
                        collected.append(item)

                    if self._should_stop(collected, mode, limit_qty, start_date):
                        break

                    if len(collected) == previous_count:
                        stable_count += 1
                    else:
                        stable_count = 0

                    if stable_count >= 3:
                        break

                    previous_count = len(collected)

                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(self.scroll_pause)

                    self._click_more(page)

                return self._filter_items(collected, mode, limit_qty, start_date, end_date)
            finally:
                context.close()
                browser.close()

    def _get_review_url(self, url: str) -> str:
        if "/review" in url:
            return url
        url = url.rstrip("/")
        return f"{url}/review/visitor"

    def _parse_items(self, soup) -> List[ReviewItem]:
        items: List[ReviewItem] = []

        review_selectors = [
            "li.pui__X35jYm",
            "li.place_apply_pui",
            "div.pui__vn15t2",
            "li[class*='review']",
            "div[class*='review']"
        ]

        for selector in review_selectors:
            elements = soup.select(selector)
            if elements:
                for item in elements:
                    text = self._extract_review_text(item)
                    if text and len(text) > 5:
                        review_date = self._extract_review_date(item)
                        items.append(ReviewItem(date=review_date, review=text))
                if items:
                    break

        if not items:
            all_text_divs = soup.select("div[class*='pui'], span[class*='pui']")
            for div in all_text_divs:
                text = div.get_text(strip=True)
                if text and 20 < len(text) < 1000 and not text.startswith("http"):
                    items.append(ReviewItem(date=date.today(), review=text))

        return items

    def _extract_review_text(self, item) -> Optional[str]:
        text_selectors = [
            "div.pui__vn15t2 a",
            "div.pui__vn15t2",
            "a.pui__vn15t2",
            "span.pui__vn15t2",
            "div[class*='content']",
            "p[class*='text']",
            "span[class*='text']"
        ]

        for selector in text_selectors:
            text_area = item.select_one(selector)
            if text_area:
                text = text_area.get_text(strip=True)
                if text:
                    if text.endswith("더보기"):
                        text = text[:-3]
                    return text

        direct_text = item.get_text(strip=True)
        if direct_text and len(direct_text) > 10:
            if direct_text.endswith("더보기"):
                direct_text = direct_text[:-3]
            return direct_text

        return None

    def _extract_review_date(self, item) -> date:
        date_patterns = [
            r"(\d{4})\.(\d{1,2})\.(\d{1,2})",
            r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일",
            r"(\d{1,2})일\s*전",
            r"(\d{1,2})주\s*전",
            r"(\d{1,2})개월\s*전"
        ]

        item_text = item.get_text()

        for pattern in date_patterns[:2]:
            match = re.search(pattern, item_text)
            if match:
                try:
                    return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                except ValueError:
                    continue

        for span in item.select("[class*='date'], [class*='time'], .pui__gfuUIT .pui__blind"):
            text = span.get_text()
            for pattern in date_patterns[:2]:
                match = re.search(pattern, text)
                if match:
                    try:
                        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    except ValueError:
                        continue

        return date.today()

    def _should_stop(
        self,
        items: List[ReviewItem],
        mode: ScrapeMode,
        limit_qty: Optional[int],
        start_date: Optional[date],
    ) -> bool:
        if mode == ScrapeMode.QTY and limit_qty is not None:
            return len(items) >= limit_qty
        if mode in (ScrapeMode.DATE, ScrapeMode.DATE_RANGE) and start_date is not None:
            oldest = min((item.date for item in items), default=date.today())
            return oldest < start_date
        return False

    def _filter_items(
        self,
        items: List[ReviewItem],
        mode: ScrapeMode,
        limit_qty: Optional[int],
        start_date: Optional[date],
        end_date: Optional[date] = None,
    ) -> List[ReviewItem]:
        if mode == ScrapeMode.QTY and limit_qty is not None:
            return items[:limit_qty]
        if mode == ScrapeMode.DATE and start_date is not None:
            return [item for item in items if item.date >= start_date]
        if mode == ScrapeMode.DATE_RANGE and start_date is not None and end_date is not None:
            return [item for item in items if start_date <= item.date <= end_date]
        return items

    def _click_more(self, page) -> None:
        more_selectors = [
            "a.fvwqf",
            "a[class*='more']",
            "button[class*='more']",
            "a.rdX0R",
            "div[class*='more'] a"
        ]

        for selector in more_selectors:
            try:
                more_button = page.query_selector(selector)
                if more_button and more_button.is_visible():
                    more_button.click()
                    page.wait_for_timeout(1000)
                    return
            except Exception:
                continue


def get_scraper() -> Scraper:
    return PlaywrightScraper()
