from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator, model_validator


class ScrapeMode(str, Enum):
    QTY = "QTY"
    DATE = "DATE"


class ReviewItem(BaseModel):
    date: date
    review: str


class ScrapeRequest(BaseModel):
    url: HttpUrl
    mode: ScrapeMode = ScrapeMode.QTY
    limit_qty: Optional[int] = None
    limit_date: Optional[date] = None

    @field_validator("limit_qty")
    @classmethod
    def validate_limit_qty(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1:
            raise ValueError("limit_qty must be >= 1")
        return value

    @model_validator(mode="after")
    def validate_limits(self) -> "ScrapeRequest":
        if self.mode == ScrapeMode.QTY and self.limit_qty is None:
            raise ValueError("limit_qty is required when mode is QTY")
        if self.mode == ScrapeMode.DATE and self.limit_date is None:
            raise ValueError("limit_date is required when mode is DATE")
        return self


class ScrapeResponse(BaseModel):
    items: List[ReviewItem]
