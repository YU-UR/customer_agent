from contextlib import contextmanager

import inflection
import uuid6
from sqlalchemy import create_engine, Column, DateTime, func, String
from sqlalchemy.orm import sessionmaker, as_declarative, declared_attr

from app.core.config import settings



engine = create_engine(settings.mysql_url)
Session = sessionmaker(bind=engine, expire_on_commit=False)

session = Session()


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls):
        return inflection.underscore(cls.__name__)

    id = Column(String(36), primary_key=True, default=uuid6.uuid7, comment="ID")
    created_time = Column(DateTime(timezone=True), default=func.now(), comment="创建时间")
    updated_time = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment="更新时间")

@contextmanager
def get_db_session():
    """Database session context manager"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
