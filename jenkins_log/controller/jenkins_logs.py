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

    if list_jobs.jobs and list_jobs.jobs:
        for job in list_jobs.jobs:
            build_info_result = extract_builds_range_task.delay(job)
            build_info = build_info_result.get()

            reports_result = report_failed_jobs_task.delay(build_info, job)
            reports = reports_result.get()
            all_reports.extend(reports)

            if build_info:
                first_build_number = build_info.firstBuild.number
                last_build_number = build_info.lastCompletedBuild.number

                for build_number in range(first_build_number, last_build_number + 1):
                    url = f"http://s6006as2917:8080/job/{job.name}/{build_number}/api/json"
                    blob_result = extract_builds_to_blob_task.delay(url)
                    return blob_result

            else:
                print(f"Nenhum build encontrado para o job: {job.name}")
