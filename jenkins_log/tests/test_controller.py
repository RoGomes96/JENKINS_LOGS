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
    mock_session_local
):
    # define um job fake com atributos name e url como strings
    job = MagicMock()
    job.name = "job1"
    job.url = "http://localhost/job1/"

    # 1) Mock Celery tasks
    mock_list_jobs.delay.return_value.get.return_value = MagicMock(jobs=[job])
    mock_extract_range.delay.return_value.get.return_value = MagicMock(
        firstBuild=MagicMock(number=1),
        lastCompletedBuild=MagicMock(number=1),
        healthReport=[],
        disabled="false"
    )
    mock_report_failed.delay.return_value.get.return_value = []

    # Simula upload bem-sucedido e URL do blob
    blob_resp = MagicMock(url="http://blob/test/1")
    mock_extract_blob.delay.return_value.get.return_value = blob_resp

    # Executa a função
    result = await processar_logs_jenkins()
    print(result)
    # Verifica retorno e efeitos no DB
    assert result is blob_resp
    session = mock_session_local.return_value
    assert session.rec_added.job_name == "job1"
    assert session.rec_added.build_number == 1
    assert session.rec_added.blob_url == blob_resp.url
    assert session.committed is True
    assert session.closed is True
