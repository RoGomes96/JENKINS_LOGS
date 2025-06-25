# tasks.py
from celery import Celery
from jenkins_log.services.blob import extract_builds_to_blob
from settings import Settings
from jenkins_log.services.jenkins import (
    jenkins_jobs_list,
    extract_builds_range,
    report_failed_jobs,
)

import asyncio

settings = Settings()

app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=getattr(settings, "CELERY_RESULT_BACKEND", None),
)


@app.task
def jenkins_jobs_list_task():
    jobs_list = jenkins_jobs_list()
    if jobs_list:
        # .model_dump() para Pydantic v2, .dict() para v1
        return jobs_list.model_dump()
    return None


@app.task
def extract_builds_range_task(job_dict):
    from jenkins_log.schemas import Job

    job = Job(**job_dict)
    result = asyncio.run(extract_builds_range(job))
    return result.model_dump() if result else None


@app.task
def report_failed_jobs_task(build_list_dict, job_dict):
    from jenkins_log.schemas import BuildsList, Job

    build_list = BuildsList(**build_list_dict)
    job = Job(**job_dict)
    result = asyncio.run(report_failed_jobs(build_list, job))
    return [r.model_dump() for r in result] if result else []


@app.task
def extract_builds_to_blob_task(url, blob_name):
    result, data_criacao_jenkins = asyncio.run(extract_builds_to_blob(url, blob_name))
    if result and hasattr(result, "url"):
        return {"url": str(result.url), "created_at_jenkins": data_criacao_jenkins}
    return None
