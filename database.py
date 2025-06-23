# db.py
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import Settings


Base = declarative_base()


class BuildRecord(Base):
    __tablename__ = "jenkins_builds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String, nullable=False)
    build_number = Column(Integer, nullable=False)
    blob_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint("job_name", "build_number", name="uq_job_build"),
    )


settings = Settings()
engine = create_engine(settings.DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
