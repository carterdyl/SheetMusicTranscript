import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.api.routes._get_queue")
def test_upload_happy_path(mock_queue):
    mock_q = MagicMock()
    mock_queue.return_value = mock_q

    with patch("app.storage.jobs.create_job"):
        resp = client.post(
            "/api/upload",
            files={"audio": ("test.wav", b"\x00" * 100, "audio/wav")},
            data={"bpm": "120", "quantization": "1/16", "split_point": "60"},
        )
    assert resp.status_code == 200
    assert "job_id" in resp.json()


def test_job_not_found():
    with patch("app.storage.jobs.get_job", return_value=None):
        resp = client.get("/api/jobs/nonexistent")
    assert resp.status_code == 404
