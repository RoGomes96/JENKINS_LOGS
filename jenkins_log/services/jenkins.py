from typing import List
import aiohttp
import requests
from database import SessionLocal
from jenkins_log.schemas import (
    BuildsList,
    Job,
    JobsList,
    ReportJob,
    ReportList
)
from settings import Settings
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

settings = Settings()


def jenkins_jobs_list() -> JobsList | None:
    try:
        response = requests.get(
            settings.JENKINS_JOBS_LIST,
            auth=(settings.USERNAME, settings.ACCESS_TOKEN)
        )
        if response.status_code == 200:
            jobs_list = JobsList(**response.json())
            return jobs_list

    except Exception as e:
        print(f"Erro ao obter os jobs no jenkins: {e}")
        return None


async def extract_builds_range(job: Job) -> BuildsList | None:
    print("Job recebido em extract_builds_range:", job)
    url = job.url + "api/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            auth=aiohttp.BasicAuth('admin', settings.ACCESS_TOKEN)
        ) as response:
            print("Resposta recebida do Jenkins:", await response.json())
            try:
                if response.status == 200:
                    build_list = BuildsList(**await response.json())
                    return build_list
            except Exception as e:
                print(
                    f"Erro ao obter builds do job {job.name} no jenkins: {e}"
                )
                return None


async def report_failed_jobs(
    build_list: BuildsList,
    job: Job
) -> List[ReportList]:
    reports: List[ReportList] = []
    session = SessionLocal()
    try:
        if build_list.disabled == "false":
            if build_list.healthReport.description.contains("falharam"):
                failed = ReportJob(
                    job_name=job["name"],
                    url=job["url"]
                )
                session.add(failed)
                report = ReportList(jobName=job["name"], url=job["url"])
                reports.append(report)
        if reports:
            session.commit()
        return reports
    finally:
        session.close()


async def extract_builds_to_blob(url: str) -> aiohttp.ClientResponse | None:
    url = url + "api/json"

    blob_service_client = BlobServiceClient.from_connection_string(
        settings.CONNECTION_STRING
    )

    blob_client = blob_service_client.get_blob_client(
        container=settings.CONTAINER_NAME, blob=settings.BLOB_NAME
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                if response.status == 200:
                    await blob_client.upload_blob(
                        response.content,
                        overwrite=True
                    )
                return response
            except Exception as e:
                print(
                    f"Erro ao obter informações da build {url} no jenkins: {e}"
                )
                return None
