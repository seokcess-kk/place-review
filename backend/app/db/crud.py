from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.db.models import Analysis, Place, Review


def get_or_create_place(session: Session, url: str) -> Place:
    place = session.query(Place).filter(Place.url == url).one_or_none()
    if place:
        return place
    place = Place(url=url)
    session.add(place)
    session.flush()
    return place


def create_review(
    session: Session,
    place: Place,
    review_text: str,
    review_date: date,
) -> Review:
    review = Review(place_id=place.id, review_text=review_text, review_date=review_date)
    session.add(review)
    session.flush()
    return review


def create_analysis(
    session: Session,
    review: Review,
    sentiment: str,
    keywords: Iterable[str],
    summary: str,
) -> Analysis:
    analysis = Analysis(
        review_id=review.id,
        sentiment=sentiment,
        keywords=list(keywords),
        summary=summary,
    )
    session.add(analysis)
    session.flush()
    return analysis


def get_latest_analysis(session: Session, review_id: int) -> Optional[Analysis]:
    return (
        session.query(Analysis)
        .filter(Analysis.review_id == review_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
