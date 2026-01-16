from __future__ import annotations

from enum import Enum
from datetime import date
from typing import Optional

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


class JobResult(BaseModel):
    review_count: int
    analyzed_count: int


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[JobResult] = None
