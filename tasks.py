from celery import Celery
from settings import Settings
from jenkins_log.services.jenkins import (
    jenkins_jobs_list,
    extract_builds_range,
    report_failed_jobs,
    extract_builds_to_blob,
)

settings = Settings()

# Cria uma instância do Celery
app = Celery("tasks", broker=settings.CELERY_BROKER_URL)


@app.task
def jenkins_jobs_list_task():
    return jenkins_jobs_list()


@app.task
def extract_builds_range_task(job):
    return extract_builds_range(job)


@app.task
def report_failed_jobs_task(build_list, job):
    return report_failed_jobs(build_list, job)


@app.task
def extract_builds_to_blob_task(url):
    return extract_builds_to_blob(url)
