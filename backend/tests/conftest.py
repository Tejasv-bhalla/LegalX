import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to path so imports work correctly inside tests
backend_dir = str(Path(__file__).resolve().parents[1])
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app

@pytest.fixture
def client():
    return TestClient(app)
