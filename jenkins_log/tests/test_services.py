import pytest
from jenkins_log.schemas import BuildsList
from jenkins_log.services.jenkins import jenkins_jobs_list
from unittest.mock import AsyncMock, patch, MagicMock


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_success(mock_get):
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

    result = jenkins_jobs_list()
    assert result.jobs[0].name == "Job1"


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_failure(mock_get):
    mock_get.side_effect = Exception("Erro na requisição")
    result = jenkins_jobs_list()
    assert result is None


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_extract_builds_range():
    from jenkins_log.services.jenkins import extract_builds_range

    # 1) Mock do response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "firstBuild": {"number": 1},
            "lastCompletedBuild": {"number": 5},
            "healthReport": [],
            "disabled": "false",
        }
    )

    # 2) Mock do context manager de session.get()
    mock_get_cm = MagicMock()
    mock_get_cm.__aenter__.return_value = mock_response
    mock_get_cm.__aexit__.return_value = None

    # 3) Mock da sessão em si
    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_cm

    # 4) Patch do ClientSession para retornar o mock_session no async with
    mock_cs = MagicMock()
    mock_cs.return_value.__aenter__.return_value = mock_session
    mock_cs.return_value.__aexit__.return_value = None

    with patch("aiohttp.ClientSession", mock_cs):
        # job de teste
        job = MagicMock()
        job.url = "http://localhost/job1/"
        job.name = "job1"

        builds = await extract_builds_range(job)

        assert isinstance(builds, BuildsList)
        assert builds.firstBuild.number == 1
        assert builds.lastCompletedBuild.number == 5


@patch("jenkins_log.services.jenkins.requests.get")
def test_jenkins_jobs_list_non_200(mock_get):
    mock_resp = MagicMock(status_code=500)
    mock_get.return_value = mock_resp

    result = jenkins_jobs_list()
    assert result is None
