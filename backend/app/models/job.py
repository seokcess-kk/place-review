from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"


class JobRequest(BaseModel):
    url: str = Field(min_length=1)
    mode: Optional[str] = None
    limit_qty: Optional[int] = Field(default=None, ge=1)


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
