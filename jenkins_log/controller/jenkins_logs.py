import asyncio
from database import BuildRecord, SessionLocal
from tasks import (
    extract_builds_range_task,
    extract_builds_to_blob_task,
    jenkins_jobs_list_task,
    report_failed_jobs_task,
)
import os


async def processar_logs_jenkins():
    print("==== INICIANDO PROCESSO DE COLETA DE LOGS DO JENKINS ====")
    all_reports = []
    print("Chamando jenkins_jobs_list_task...")
    list_jobs = jenkins_jobs_list_task.delay().get()
    print(f"Resultado list_jobs: {list_jobs}")
    if not list_jobs or "jobs" not in list_jobs or not list_jobs["jobs"]:
        print("Nenhum job retornado pelo Jenkins")
        return None
    jobs_list = list_jobs["jobs"]

    # limita a quantidade de jobs via env var (0 = sem limite)
    max_jobs = int(os.getenv("MAX_JOBS", "0"))
    jobs_iter = jobs_list[:max_jobs] if max_jobs > 0 else jobs_list

    db = SessionLocal()
    try:
        for job in jobs_iter:
            print(f"Processando job: {job}")
            build_info = extract_builds_range_task.delay(job).get()
            print(f"Resultado build_info: {build_info}")
            if not build_info:
                print(f"Nenhum build para {job['name']}")
                continue

            reports = report_failed_jobs_task.delay(build_info, job).get()
            if reports:
                all_reports.extend(reports)

            start = build_info["firstBuild"]["number"]
            end = build_info["lastCompletedBuild"]["number"]

            for num in range(start, end + 1):
                # Checagem do Banco de Dados
                exists = db.query(BuildRecord)\
                           .filter_by(job_name=job["name"], build_number=num)\
                           .first()
                if exists:
                    continue

                url = f"http://jenkins:8080/job/{job['name']}/{num}/api/json"
                print(f"ulr:{url}")
                blob_result = extract_builds_to_blob_task.delay(url).get()
                if blob_result:
                    rec = BuildRecord(
                        job_name=job["name"],
                        build_number=num,
                        blob_url=blob_result.get("url") if isinstance(blob_result, dict) else blob_result.url
                    )
                    db.add(rec)
                    db.commit()

        return all_reports

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(processar_logs_jenkins())
