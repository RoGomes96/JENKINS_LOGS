from jenkins_log.services.jenkins import (
    extract_builds_info,
    extract_builds_range,
    jenkins_jobs_list,
    report_failed_jobs,
)


async def processar_logs_jenkins():
    all_reports = []

    list_jobs = jenkins_jobs_list()

    if list_jobs.jobs and list_jobs.jobs:
        for job in list_jobs.jobs:

            build_info = await extract_builds_range(job)
            reports = await report_failed_jobs(build_info, job)
            all_reports.extend(reports)

            if build_info:

                first_build_number = build_info.firstBuild.number
                last_build_number = build_info.lastCompletedBuild.number

                for build_number in range(first_build_number, last_build_number + 1):

                    url = f"http://s6006as2917:8080/job/{job.name}/{build_number}/api/json"
                    build_info = await extract_builds_info(url)
                    return build_info

            else:

                print(f"Nenhum build encontrado para o job: {job.name}")
