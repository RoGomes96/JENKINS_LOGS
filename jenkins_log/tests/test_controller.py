import pytest
from unittest.mock import patch, MagicMock
from jenkins_log.controller.jenkins_logs import processar_logs_jenkins


@pytest.mark.asyncio
@patch("jenkins_log.controller.jenkins_logs.jenkins_jobs_list_task")
@patch("jenkins_log.controller.jenkins_logs.extract_builds_range_task")
@patch("jenkins_log.controller.jenkins_logs.report_failed_jobs_task")
@patch("jenkins_log.controller.jenkins_logs.extract_builds_to_blob_task")
async def test_processar_logs_jenkins(
    mock_extract_blob, mock_report_failed, mock_extract_range, mock_list_jobs
):
    mock_list_jobs.delay.return_value.get.return_value = MagicMock(
        jobs=[MagicMock(name="job1", url="http://localhost/job1/")]
    )

    mock_extract_range.delay.return_value.get.return_value = MagicMock(
        firstBuild=MagicMock(number=1),
        lastCompletedBuild=MagicMock(number=1),
        healthReport=[],
        disabled="false",
    )

    mock_report_failed.delay.return_value.get.return_value = []
    mock_extract_blob.delay.return_value = "blob_result"

    result = await processar_logs_jenkins()

    assert result == "blob_result"
