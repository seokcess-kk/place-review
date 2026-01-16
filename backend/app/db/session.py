from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings
from app.db.base import Base


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session() -> Session:
    engine = get_engine()
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return session_factory()


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
