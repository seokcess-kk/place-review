from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class SentimentLabel(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class AnalyzeRequest(BaseModel):
    review: str = Field(min_length=1, max_length=2000)


class AnalyzeResponse(BaseModel):
    sentiment: SentimentLabel
    keywords: List[str]
    summary: str
