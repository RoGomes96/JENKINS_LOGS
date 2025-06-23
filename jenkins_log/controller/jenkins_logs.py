from database import BuildRecord, SessionLocal
from tasks import (
    extract_builds_range_task,
    extract_builds_to_blob_task,
    jenkins_jobs_list_task,
    report_failed_jobs_task,
)


async def processar_logs_jenkins():
    all_reports = []

    result = jenkins_jobs_list_task.delay()
    list_jobs = result.get()

    if not list_jobs or not list_jobs.jobs:
        return None

    db = SessionLocal()
    try:
        for job in list_jobs.jobs:
            build_info = extract_builds_range_task.delay(job).get()

            reports = report_failed_jobs_task.delay(build_info, job).get()

            all_reports.extend(reports)

            if not build_info:
                print(f"Nenhum build para {job.name}")
                continue

            start = build_info.firstBuild.number
            end = build_info.lastCompletedBuild.number

            for num in range(start, end + 1):
                # Checagem do Banco de Dados
                exists = db.query(BuildRecord)\
                            .filter_by(job_name=job.name, build_number=num)\
                            .first()
                if exists:
                    continue

                url = f"http://s6006as2917:8080/job/{job.name}/{num}/api/json"
                blob_result = extract_builds_to_blob_task.delay(url).get()
                if blob_result:
                    rec = BuildRecord(
                        job_name=job.name,
                        build_number=num,
                        blob_url=blob_result.url
                    )
                    db.add(rec)
                    db.commit()

                    return blob_result

        return None

    finally:
        db.close()
