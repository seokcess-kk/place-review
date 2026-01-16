from __future__ import annotations

from enum import Enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.scrape import ScrapeMode


class JobStatus(str, Enum):
    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"


class JobRequest(BaseModel):
    place_id: str = Field(min_length=1)
    mode: Optional[ScrapeMode] = None
    limit_qty: Optional[int] = Field(default=None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_limits(self) -> "JobRequest":
        if self.mode == ScrapeMode.QTY and self.limit_qty is None:
            raise ValueError("limit_qty is required when mode is QTY")
        if self.mode == ScrapeMode.DATE and self.start_date is None:
            raise ValueError("start_date is required when mode is DATE")
        if self.mode == ScrapeMode.DATE_RANGE:
            if self.start_date is None or self.end_date is None:
                raise ValueError("start_date and end_date are required when mode is DATE_RANGE")
            if self.start_date > self.end_date:
                raise ValueError("start_date must be before or equal to end_date")
        return self

    def get_url(self) -> str:
        return f"https://m.place.naver.com/place/{self.place_id}"


class AspectData(BaseModel):
    aspect: str
    sentiment: str


class ReviewData(BaseModel):
    id: int
    text: str
    date: str
    sentiment: Optional[str] = None
    aspects: List[AspectData] = []
    keywords: List[str] = []
    summary: Optional[str] = None


class JobResult(BaseModel):
    place_id: Optional[int] = None
    place_url: Optional[str] = None
    review_count: int
    analyzed_count: int
    reviews: List[ReviewData] = []


class JobProgress(BaseModel):
    current: int = 0
    total: int = 0
    stage: str = "pending"
    percent: int = 0


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[JobProgress] = None
    result: Optional[JobResult] = None
    error: Optional[str] = None
