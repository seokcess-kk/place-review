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
    url: str = Field(min_length=1)
    mode: Optional[ScrapeMode] = None
    limit_qty: Optional[int] = Field(default=None, ge=1)
    limit_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_limits(self) -> "JobRequest":
        if self.mode == ScrapeMode.QTY and self.limit_qty is None:
            raise ValueError("limit_qty is required when mode is QTY")
        if self.mode == ScrapeMode.DATE and self.limit_date is None:
            raise ValueError("limit_date is required when mode is DATE")
        return self


class ReviewData(BaseModel):
    id: int
    text: str
    date: str
    sentiment: Optional[str] = None
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
