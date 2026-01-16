from __future__ import annotations

import json
import os
from importlib.util import find_spec
from typing import Protocol

from app.models.analyze import AnalyzeResponse, SentimentLabel


class AnalyzerConfigError(ValueError):
    pass


class AnalyzerDependencyError(RuntimeError):
    pass


class Analyzer(Protocol):
    def analyze(self, review: str) -> AnalyzeResponse:
        ...


class OpenAIAnalyzer:
    def analyze(self, review: str) -> AnalyzeResponse:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AnalyzerConfigError("OPENAI_API_KEY is required")
        if find_spec("openai") is None:
            raise AnalyzerDependencyError("OpenAI SDK is missing; install openai")

        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = (
            "Review: \"{review}\"\n"
            "Output JSON only:\n"
            "{\n"
            '    "sentiment": "Positive" or "Negative" or "Neutral",\n'
            '    "keywords": ["key1", "key2", "key3"],\n'
            '    "summary": "One sentence summary in Korean"\n'
            "}"
        ).format(review=review)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "JSON Output Mode"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        payload = response.choices[0].message
        if payload.content is None:
            raise AnalyzerDependencyError("OpenAI response missing content")
        try:
            data = json.loads(payload.content)
        except json.JSONDecodeError as exc:
            raise AnalyzerDependencyError("OpenAI response is not valid JSON") from exc
        if not isinstance(data, dict):
            raise AnalyzerDependencyError("OpenAI response JSON must be an object")
        if "sentiment" not in data or "keywords" not in data or "summary" not in data:
            raise AnalyzerDependencyError("OpenAI response missing required fields")
        return AnalyzeResponse(
            sentiment=SentimentLabel(data["sentiment"]),
            keywords=list(data["keywords"]),
            summary=str(data["summary"]),
        )


def get_analyzer() -> Analyzer:
    return OpenAIAnalyzer()
