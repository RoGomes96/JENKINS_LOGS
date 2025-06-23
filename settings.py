import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    JENKINS_JOBS_LIST: str
    USERNAME: str
    ACCESS_TOKEN: str
    CONNECTION_STRING: str
    CONTAINER_NAME: str
    BLOB_NAME: str
    CELERY_BROKER_URL: str
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./builds.db")
