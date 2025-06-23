from typing import List
import aiohttp
import requests
from jenkins_log.schemas import BuildsList, Job, JobsList, ReportJob, ReportList
from settings import Settings

settings = Settings()


def jenkins_jobs_list():
    try:
        response = requests.get(
            settings.JENKINS_JOBS_LIST, auth=(settings.USERNAME, settings.ACCESS_TOKEN)
        )
        if response.status_code == 200:
            jobs_list = JobsList(**response.json())
            return jobs_list

    except Exception as e:
        print(f"Erro ao obter os jobs no jenkins: {e}")
        return None


async def extract_builds_range(job):
    url = job.url + "api/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                if response.status == 200:
                    build_list = BuildsList(**await response.json())
                    return build_list
            except Exception as e:
                print(f"Erro ao obter os builds do job {job.name} no jenkins: {e}")
                return None


async def report_failed_jobs(build_list: BuildsList, job: Job) -> List[ReportList]:
    reports = []
    if build_list.disable == 'false':

        if build_list.healthReport.description.contains('falharam'):

            report = ReportJob(jobName=job.name, url=job.url)
            reports.append(report)

    return reports


async def extract_builds_info(url):
    url = url + "api/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                if response.status == 200:
                    response = await response.json()
                    return response
            except Exception as e:
                print(f"Erro ao obter as informações da build {url} no jenkins: {e}")
                return None
