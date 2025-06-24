import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

import jenkins_log.controller.jenkins_logs as jl
import database
from database import BuildRecord
from jenkins_log.controller.jenkins_logs import processar_logs_jenkins


class TestesLog:
    @pytest.fixture(autouse=True)
    def _override_sessionlocal(self, db_engine, monkeypatch):
        # Usa o SessionLocal do módulo database (já pelo fixture db_engine)
        monkeypatch.setattr(jl, "SessionLocal", database.SessionLocal)

    @pytest.mark.asyncio
    async def test_newblob_process_logs(self):
        """
        - Quando há uma build nova, ela é enviada ao blob e inserida no banco.
        """
        # Arrange: Mock Celery tasks
        m = pytest.MonkeyPatch()
        m.setattr(
            jl, "jenkins_jobs_list_task",
            MagicMock(delay=lambda: MagicMock(get=lambda: {
                "jobs": [
                    {"name": "job1", "url": "http://localhost/job1/"}
                ]
            }))
        )
        m.setattr(
            jl, "extract_builds_range_task",
            MagicMock(delay=lambda job: MagicMock(get=lambda: {
                "firstBuild": {"number": 1},
                "lastCompletedBuild": {"number": 1},
                "healthReport": [],
                "disabled": False
            }))
        )
        m.setattr(
            jl, "report_failed_jobs_task",
            MagicMock(delay=lambda *args: MagicMock(get=lambda: []))
        )
        fake_blob = {"url": "http://blob/test/1"}
        m.setattr(
            jl, "extract_builds_to_blob_task",
            MagicMock(delay=lambda url: MagicMock(get=lambda: fake_blob))
        )

        # Act
        result = await processar_logs_jenkins()

        # Assert
        assert isinstance(result, list)

        # Verifica no DB de teste
        db = database.SessionLocal()
        recs = db.query(BuildRecord).all()
        assert len(recs) == 1
        assert recs[0].job_name == "job1"
        assert recs[0].build_number == 1
        assert recs[0].blob_url == "http://blob/test/1"
        db.close()
        m.undo()

    @pytest.mark.asyncio
    async def test_existent_log_process(self):
        """
        - Quando a build já existe no DB, não chama o task de blob.
        """
        # Arrange: Insere registro pré-existente no DB de teste
        db = database.SessionLocal()
        db.add(BuildRecord(job_name="job1", build_number=1, blob_url="old"))
        db.commit()
        db.close()

        # Mock Celery tasks
        m = pytest.MonkeyPatch()
        m.setattr(
            jl, "jenkins_jobs_list_task",
            MagicMock(delay=lambda: MagicMock(get=lambda: {
                "jobs": [
                    {"name": "job1", "url": "http://localhost/job1/"}
                ]
            }))
        )
        m.setattr(
            jl, "extract_builds_range_task",
            MagicMock(delay=lambda job: MagicMock(get=lambda: {
                "firstBuild": {"number": 1},
                "lastCompletedBuild": {"number": 1},
                "healthReport": [],
                "disabled": False
            }))
        )
        m.setattr(
            jl, "report_failed_jobs_task",
            MagicMock(delay=lambda *args: MagicMock(get=lambda: []))
        )

        called = False

        def spy_delay(url):
            nonlocal called
            called = True
            return MagicMock(get=lambda: None)

        m.setattr(
            jl, "extract_builds_to_blob_task",
            MagicMock(delay=spy_delay)
        )

        # Act
        result = await processar_logs_jenkins()

        # Assert
        assert result == []
        assert called is False
        m.undo()

    @pytest.mark.asyncio
    async def test_no_jobs_return_none(self):
        """
        - Quando não há jobs, retorna None sem criar registros.
        """
        # Arrange: Mock lista vazia
        m = pytest.MonkeyPatch()
        m.setattr(
            jl, "jenkins_jobs_list_task",
            MagicMock(delay=lambda: MagicMock(get=lambda: {
                "jobs": [
                ]
            }))
        )

        # Act
        result = await processar_logs_jenkins()

        # Assert
        assert result is None
        db = database.SessionLocal()
        recs = db.query(BuildRecord).all()
        assert recs == []
        db.close()
        m.undo()
