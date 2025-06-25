import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    JENKINS_JOBS_LIST: str
    USERNAME: str
    ACCESS_TOKEN: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db")
    URL_BLOB: str
    CONTAINER_NAME: str
    SAS_TOKEN: str
    MAX_JOBS: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
