# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database  # seu módulo database.py


@pytest.fixture(scope="function")
def db_engine(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    url = f"sqlite:///{db_file}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    database.Base.metadata.create_all(engine)

    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    monkeypatch.setattr(database, "SessionLocal", TestSessionLocal)

    yield engine

    database.Base.metadata.drop_all(engine)


# FakeSession to simulate SQLAlchemy session behavior
class FakeSession:
    def __init__(self):
        self.rec_added = None
        self.committed = False
        self.closed = False

    def query(self, model):
        return self

    def filter_by(self, **kwargs):
        return self

    def first(self):
        # Simula: nenhum registro existente
        return None

    def add(self, rec):
        # Captura o record adicionado
        self.rec_added = rec

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True
