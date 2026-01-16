from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from importlib.util import find_spec
from typing import List, Optional, Protocol

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
    def scrape(
        self,
        url: str,
        mode: ScrapeMode,
        limit_qty: Optional[int],
        limit_date: Optional[date],
    ) -> List[ReviewItem]:
        if mode == ScrapeMode.QTY and limit_qty is None:
            raise ScraperConfigError("limit_qty is required when mode is QTY")
        if mode == ScrapeMode.DATE and limit_date is None:
            raise ScraperConfigError("limit_date is required when mode is DATE")
        if find_spec("selenium") is None or find_spec("webdriver_manager") is None:
            raise ScraperDependencyError(
                "Selenium dependencies are missing; install selenium and webdriver-manager"
            )
        if find_spec("bs4") is None:
            raise ScraperDependencyError("BeautifulSoup is missing; install beautifulsoup4")

        from bs4 import BeautifulSoup
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

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
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for item in soup.select("li.place_apply_pui"):
                text_area = item.select_one("div.pui__vn15t2 a")
                if not text_area:
                    continue
                text = text_area.get_text(strip=True)
                if text.endswith("더보기"):
                    text = text[:-3]
                items.append(ReviewItem(date=date.today(), review=text))
            return items[: limit_qty or len(items)]
        finally:
            driver.quit()


def get_scraper() -> Scraper:
    return SeleniumScraper()
