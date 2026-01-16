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
class SeleniumScraper:
    max_scrolls: int = 12
    scroll_pause: float = 1.25

    def scrape(
        self,
        url: str,
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> List[ReviewItem]:
        if find_spec("selenium") is None or find_spec("webdriver_manager") is None:
            raise ScraperDependencyError(
                "Selenium dependencies are missing; install selenium and webdriver-manager"
            )
        if find_spec("bs4") is None:
            raise ScraperDependencyError("BeautifulSoup is missing; install beautifulsoup4")

        if mode == ScrapeMode.QTY and limit_qty is None:
            raise ScraperConfigError("limit_qty is required when mode is QTY")
        if mode == ScrapeMode.DATE and limit_date is None:
            raise ScraperConfigError("limit_date is required when mode is DATE")

        from bs4 import BeautifulSoup
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        try:
            driver.get(str(url))
            seen_keys: set[tuple[date, str]] = set()
            collected: List[ReviewItem] = []
            stable_count = 0
            previous_count = 0
            for _ in range(self.max_scrolls):
                html = driver.page_source
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
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.scroll_pause)
                self._click_more(driver)
            return self._filter_items(collected, mode, limit_qty, limit_date)
        finally:
            driver.quit()

    @staticmethod
    def _parse_items(raw_items: Iterable) -> List[ReviewItem]:
        items: List[ReviewItem] = []
        for item in raw_items:
            text = SeleniumScraper._extract_review_text(item)
            if not text:
                continue
            review_date = SeleniumScraper._extract_review_date(item)
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
            parsed = SeleniumScraper._parse_korean_date(span.text)
            if parsed:
                return parsed
        return date.today()

    @staticmethod
    def _parse_korean_date(text: str) -> Optional[date]:
        match = re.search(r"(\\d{4})년\\s*(\\d{1,2})월\\s*(\\d{1,2})일", text)
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
    def _click_more(driver) -> None:
        try:
            button = driver.find_element("css selector", "a.fvwqf")
            button.click()
        except Exception:
            return


def get_scraper() -> Scraper:
    return SeleniumScraper()
