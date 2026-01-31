import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.routes._get_queue")
@patch("app.api.routes.create_job")
def test_upload_happy_path(mock_create, mock_queue):
    mock_queue.return_value = MagicMock()

    resp = client.post(
        "/api/upload",
        files={"audio": ("test.wav", b"\x00" * 100, "audio/wav")},
        data={"bpm": "120", "quantization": "1/16", "split_point": "60"},
    )
    assert resp.status_code == 200
    assert "job_id" in resp.json()


@patch("app.api.routes.get_job", return_value=None)
def test_job_not_found(mock_get):
    resp = client.get("/api/jobs/nonexistent")
    assert resp.status_code == 404
