import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from functools import wraps
from typing import Generator

SessionLocal = None
Base: DeclarativeMeta = declarative_base()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def with_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with session_scope() as session:
            try:
                result = f(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise e

    return wrapper


def get_db() -> Generator[Session, None, None]:
    """Yield a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db0() -> Session:
    return SessionLocal()


def init_database(config: dict):
    global SessionLocal

    engine = create_engine(
        config.get('uri'),
        json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
