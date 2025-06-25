import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jenkins_log.schemas import BuildsList
from jenkins_log.services.jenkins import (
    jenkins_jobs_list,
    extract_builds_range
)


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_success(mock_get):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jobs": [
            {
                "_class": "hudson.model.FreeStyleProject",
                "name": "Job1",
                "url": "http://localhost/job1/",
            }
        ]
    }
    mock_get.return_value = mock_response

    # Act
    result = jenkins_jobs_list()

    # Assert
    assert len(result.jobs) == 1
    job = result.jobs[0]
    assert job.name == "Job1"
    assert job.url == "http://localhost/job1/"


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_failure(mock_get):
    # Arrange
    mock_get.side_effect = Exception("Erro na requisição")

    # Act
    result = jenkins_jobs_list()

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_extract_builds_range():
    # Arrange
    # 1) mock da resposta JSON
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "firstBuild": {"number": 1},
        "lastCompletedBuild": {"number": 5},
        "healthReport": [],
        "disabled": False,
    })

    # 2) context manager para session.get()
    mock_get_cm = AsyncMock()
    mock_get_cm.__aenter__.return_value = mock_response
    mock_get_cm.__aexit__.return_value = None

    # 3) sessão mock
    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_cm

    # 4) patch do ClientSession no módulo correto
    client_session_cm = AsyncMock()
    client_session_cm.__aenter__.return_value = mock_session
    client_session_cm.__aexit__.return_value = None

    # Act
    with patch(
        "jenkins_log.services.jenkins.aiohttp.ClientSession",
        return_value=client_session_cm,
    ):
        job = MagicMock(url="http://localhost/job1/", name="job1")
        builds = await extract_builds_range(job)

        # Assert
        assert isinstance(builds, BuildsList)
        assert builds.firstBuild.number == 1
        assert builds.lastCompletedBuild.number == 5


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_non_200(mock_get):
    # Arrange
    mock_resp = MagicMock(status_code=500)
    mock_get.return_value = mock_resp

    # Act
    result = jenkins_jobs_list()

    # Assert
    assert result is None
