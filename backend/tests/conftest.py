import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Point the app at an isolated SQLite file BEFORE importing it so settings and
# the engine pick it up. Behaviour matches the seeded PostgreSQL deployment.
_DB = Path(tempfile.gettempdir()) / "busgap_test.db"
if _DB.exists():
    _DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_DB}"
os.environ["SEED_ON_EMPTY"] = "true"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    if _DB.exists():
        _DB.unlink()
