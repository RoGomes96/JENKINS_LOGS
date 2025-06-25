from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
from jenkins_log.controller.jenkins_logs import processar_logs_jenkins
from jenkins_log.tests.conftest import FakeSession


@pytest.mark.asyncio
@patch("jenkins_log.controller.jenkins_logs.SessionLocal", return_value=FakeSession())
@patch("jenkins_log.controller.jenkins_logs.jenkins_jobs_list_task")
@patch("jenkins_log.controller.jenkins_logs.extract_builds_range_task")
@patch("jenkins_log.controller.jenkins_logs.report_failed_jobs_task")
@patch("jenkins_log.controller.jenkins_logs.extract_builds_to_blob_task")
async def test_processar_logs_jenkins(
    mock_extract_blob,
    mock_report_failed,
    mock_extract_range,
    mock_list_jobs,
    mock_session_local,
):
    # Arrange
    job = {"name": "job1", "url": "http://localhost/job1/"}
    mock_list_jobs.delay.return_value.get.return_value = {"jobs": [job]}
    # 1) Mock Celery tasks
    mock_extract_range.delay.return_value.get.return_value = {
        "firstBuild": {"number": 1},
        "lastCompletedBuild": {"number": 1},
        "healthReport": [],
        "disabled": False,
    }
    mock_report_failed.delay.return_value.get.return_value = []

    # Simula upload bem-sucedido e URL do blob
    blob_resp = {
        "url": "http://blob/test/1",
        "created_at_jenkins": datetime(2022, 3, 17, 12, 14, 12, 175000),
    }
    mock_extract_blob.delay.return_value.get.return_value = blob_resp

    # Act
    result = await processar_logs_jenkins()

    # Assert
    assert isinstance(result, list)
    session = mock_session_local.return_value
    assert session.rec_added.job_name == "job1"
    assert session.rec_added.build_number == 1
    assert session.rec_added.blob_url == blob_resp["url"]
    assert session.committed is True
    assert session.closed is True
