from __future__ import annotations

import json
import os
from importlib.util import find_spec
from typing import Protocol, Optional

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
        api_key = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL")

        if not api_key:
            raise AnalyzerConfigError("OpenAI API key is required (AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY)")

        if find_spec("openai") is None:
            raise AnalyzerDependencyError("OpenAI SDK is missing; install openai")

        from openai import OpenAI

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)

        prompt = f"""다음 한국어 리뷰를 분석해주세요.

리뷰: "{review}"

다음 JSON 형식으로만 응답하세요:
{{
    "sentiment": "Positive" 또는 "Negative" 또는 "Neutral",
    "keywords": ["핵심키워드1", "핵심키워드2", "핵심키워드3"],
    "summary": "한 문장으로 요약된 리뷰 내용"
}}

sentiment 판단 기준:
- Positive: 만족, 추천, 칭찬, 긍정적 경험
- Negative: 불만, 비추천, 비판, 부정적 경험
- Neutral: 중립적 의견, 사실 전달만

keywords는 리뷰에서 가장 중요한 3개 키워드를 추출하세요.
summary는 리뷰 핵심 내용을 한국어 한 문장으로 요약하세요."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 한국어 리뷰 분석 전문가입니다. JSON 형식으로만 응답합니다."},
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

        sentiment_map = {
            "positive": SentimentLabel.POSITIVE,
            "negative": SentimentLabel.NEGATIVE,
            "neutral": SentimentLabel.NEUTRAL,
        }
        sentiment_raw = str(data["sentiment"]).lower()
        sentiment = sentiment_map.get(sentiment_raw, SentimentLabel.NEUTRAL)

        return AnalyzeResponse(
            sentiment=sentiment,
            keywords=list(data["keywords"])[:5],
            summary=str(data["summary"]),
        )


class FallbackAnalyzer:
    POSITIVE_WORDS = ["좋", "만족", "추천", "감사", "친절", "최고", "굿", "훌륭", "맛있", "깨끗"]
    NEGATIVE_WORDS = ["나쁘", "불만", "별로", "실망", "안좋", "짜증", "최악", "비추", "불친절", "더럽"]

    def analyze(self, review: str) -> AnalyzeResponse:
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in review)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in review)

        if positive_count > negative_count:
            sentiment = SentimentLabel.POSITIVE
        elif negative_count > positive_count:
            sentiment = SentimentLabel.NEGATIVE
        else:
            sentiment = SentimentLabel.NEUTRAL

        words = review.replace(",", " ").replace(".", " ").split()
        keywords = [w for w in words if len(w) >= 2][:3]

        summary = review[:50] + "..." if len(review) > 50 else review

        return AnalyzeResponse(
            sentiment=sentiment,
            keywords=keywords,
            summary=summary,
        )


def get_analyzer() -> Analyzer:
    api_key = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIAnalyzer()
    return FallbackAnalyzer()
