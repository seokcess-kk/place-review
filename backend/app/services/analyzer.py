from __future__ import annotations

import json
import os
from importlib.util import find_spec
from typing import Protocol

from app.models.analyze import AnalyzeResponse, AspectSentiment, SentimentLabel


class AnalyzerConfigError(ValueError):
    pass


class AnalyzerDependencyError(RuntimeError):
    pass


class Analyzer(Protocol):
    def analyze(self, review: str) -> AnalyzeResponse:
        ...


FEW_SHOT_EXAMPLES = """
[예시 1 - 긍정]
리뷰: "직원분이 정말 친절하시고 음식도 너무 맛있었어요. 다음에 또 올게요!"
분석:
{
    "sentiment": "Positive",
    "aspects": [
        {"aspect": "서비스", "sentiment": "Positive"},
        {"aspect": "음식", "sentiment": "Positive"}
    ],
    "keywords": ["친절", "맛있다", "재방문"],
    "summary": "친절한 서비스와 맛있는 음식에 만족하여 재방문 의사를 밝힘"
}

[예시 2 - 부정]
리뷰: "주차가 너무 불편하고 가격도 비싸요. 음식은 그냥 평범했습니다."
분석:
{
    "sentiment": "Negative",
    "aspects": [
        {"aspect": "주차", "sentiment": "Negative"},
        {"aspect": "가격", "sentiment": "Negative"},
        {"aspect": "음식", "sentiment": "Neutral"}
    ],
    "keywords": ["주차", "비싸다", "평범"],
    "summary": "주차 불편과 비싼 가격에 불만족, 음식은 평범한 수준"
}

[예시 3 - 중립]
리뷰: "음식은 맛있었는데 배달이 늦어서 식어서 왔어요."
분석:
{
    "sentiment": "Neutral",
    "aspects": [
        {"aspect": "음식", "sentiment": "Positive"},
        {"aspect": "배달", "sentiment": "Negative"}
    ],
    "keywords": ["맛있다", "배달 늦음", "식음"],
    "summary": "음식 맛은 좋았으나 배달 지연으로 식어서 도착"
}
"""

SYSTEM_PROMPT = """당신은 전문적인 한국어 리뷰 감정 분석가입니다.

[분석 가이드라인]
1. 감정 판단 기준:
   - Positive: 명시적인 칭찬, 만족, 추천, 재방문 의사 표현
   - Negative: 불만, 비추천, 비판, 부정적 경험 표현
   - Neutral: 장단점이 섞여있거나, 단순 사실 나열, 판단이 어려운 경우

2. Aspect(속성) 추출:
   - 리뷰에서 언급된 구체적인 속성(음식, 서비스, 가격, 분위기, 청결, 배달 등)을 식별
   - 각 속성에 대한 개별 감정을 판단
   - 언급되지 않은 속성은 포함하지 않음

3. 키워드 추출:
   - 리뷰의 핵심을 나타내는 2-4개 키워드
   - 형용사, 명사 위주로 추출

4. 요약:
   - 리뷰 핵심 내용을 한 문장으로 요약
   - 객관적이고 간결하게 작성

반드시 JSON 형식으로만 응답하세요."""


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

        user_prompt = f"""{FEW_SHOT_EXAMPLES}

이제 아래 리뷰를 분석해주세요.

리뷰: "{review}"

위 예시와 동일한 JSON 형식으로 분석 결과를 출력하세요:
{{
    "sentiment": "Positive" 또는 "Negative" 또는 "Neutral",
    "aspects": [{{"aspect": "속성명", "sentiment": "Positive/Negative/Neutral"}}, ...],
    "keywords": ["키워드1", "키워드2", ...],
    "summary": "한 문장 요약"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
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

        aspects = []
        if "aspects" in data and isinstance(data["aspects"], list):
            for asp in data["aspects"]:
                if isinstance(asp, dict) and "aspect" in asp and "sentiment" in asp:
                    asp_sentiment_raw = str(asp["sentiment"]).lower()
                    asp_sentiment = sentiment_map.get(asp_sentiment_raw, SentimentLabel.NEUTRAL)
                    aspects.append(AspectSentiment(
                        aspect=str(asp["aspect"]),
                        sentiment=asp_sentiment,
                    ))

        return AnalyzeResponse(
            sentiment=sentiment,
            aspects=aspects,
            keywords=list(data["keywords"])[:5],
            summary=str(data["summary"]),
        )


class FallbackAnalyzer:
    POSITIVE_WORDS = ["좋", "만족", "추천", "감사", "친절", "최고", "굿", "훌륭", "맛있", "깨끗"]
    NEGATIVE_WORDS = ["나쁘", "불만", "별로", "실망", "안좋", "짜증", "최악", "비추", "불친절", "더럽"]
    
    ASPECT_KEYWORDS = {
        "음식": ["음식", "맛", "메뉴", "요리", "반찬"],
        "서비스": ["서비스", "직원", "응대", "친절", "불친절"],
        "가격": ["가격", "비싸", "저렴", "가성비"],
        "분위기": ["분위기", "인테리어", "깔끔", "청결"],
        "배달": ["배달", "포장", "빠르", "늦"],
    }

    def analyze(self, review: str) -> AnalyzeResponse:
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in review)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in review)

        if positive_count > negative_count:
            sentiment = SentimentLabel.POSITIVE
        elif negative_count > positive_count:
            sentiment = SentimentLabel.NEGATIVE
        else:
            sentiment = SentimentLabel.NEUTRAL

        aspects = []
        for aspect_name, keywords in self.ASPECT_KEYWORDS.items():
            if any(kw in review for kw in keywords):
                aspect_positive = sum(1 for w in self.POSITIVE_WORDS if w in review)
                aspect_negative = sum(1 for w in self.NEGATIVE_WORDS if w in review)
                if aspect_positive > aspect_negative:
                    asp_sentiment = SentimentLabel.POSITIVE
                elif aspect_negative > aspect_positive:
                    asp_sentiment = SentimentLabel.NEGATIVE
                else:
                    asp_sentiment = SentimentLabel.NEUTRAL
                aspects.append(AspectSentiment(aspect=aspect_name, sentiment=asp_sentiment))

        words = review.replace(",", " ").replace(".", " ").split()
        keywords = [w for w in words if len(w) >= 2][:3]

        summary = review[:50] + "..." if len(review) > 50 else review

        return AnalyzeResponse(
            sentiment=sentiment,
            aspects=aspects,
            keywords=keywords,
            summary=summary,
        )


def get_analyzer() -> Analyzer:
    api_key = os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIAnalyzer()
    return FallbackAnalyzer()
