# db.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    create_engine,
    func,
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
    created_at_jenkins = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    __table_args__ = (
        UniqueConstraint("job_name", "build_number", name="uq_job_build"),
    )


class FailedJobReport(Base):
    __tablename__ = "failed_job_reports"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


settings = Settings()
engine = create_engine(
    settings.DB_URL,
    # apenas para SQLite; Postgres ignora
    connect_args={"check_same_thread": False}
    if settings.DB_URL.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(engine)
