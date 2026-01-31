import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from redis import Redis
from rq import Queue

from app.config import UPLOAD_DIR, OUTPUT_DIR, MAX_UPLOAD_BYTES, REDIS_URL
from app.storage.jobs import create_job, get_job

logger = logging.getLogger(__name__)
router = APIRouter()

_queue: Queue | None = None

def _get_queue() -> Queue:
    global _queue
    if _queue is None:
        _queue = Queue(connection=Redis.from_url(REDIS_URL))
    return _queue


@router.post("/upload")
async def upload(
    audio: UploadFile = File(...),
    bpm: int = Form(0),
    quantization: str = Form("1/16"),
    split_point: int = Form(60),
    semitones: int = Form(0),
):
    data = await audio.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large (max 20 MB)")

    ext = Path(audio.filename or "audio.wav").suffix.lower()
    if ext not in (".wav", ".mp3", ".flac", ".ogg"):
        raise HTTPException(400, "Unsupported audio format")

    job_id = uuid.uuid4().hex
    audio_path = UPLOAD_DIR / f"{job_id}{ext}"
    audio_path.write_bytes(data)

    if not (-12 <= semitones <= 12):
        raise HTTPException(400, "semitones must be between -12 and +12")

    params = {
        "job_id": job_id,
        "audio_path": str(audio_path),
        "bpm": bpm,
        "quantization": quantization,
        "split_point": split_point,
        "semitones": semitones,
    }
    create_job(job_id, params)
    _get_queue().enqueue("worker.run_pipeline", params, job_timeout="30m")
    logger.info("Enqueued job %s", job_id)
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    params = job.get("params", {})
    semitones = params.get("semitones", 0) if isinstance(params, dict) else 0
    resp: dict = {
        "status": job["status"],
        "progress": job["progress"],
        "semitones": semitones,
    }
    if job["status"] == "error":
        resp["error"] = job.get("error", "Unknown error")
    if "outputs" in job and isinstance(job["outputs"], dict):
        base = f"/api/jobs/{job_id}/download"
        resp["outputs"] = {}
        for kind in ("midi", "musicxml", "pdf"):
            if job["outputs"].get(kind):
                resp["outputs"][f"{kind}_url"] = f"{base}/{kind}"
    return resp


@router.get("/jobs/{job_id}/download/{kind}")
def download(job_id: str, kind: str):
    if kind not in ("midi", "musicxml", "pdf"):
        raise HTTPException(400, "Invalid kind")
    job = get_job(job_id)
    if not job or job["status"] != "done":
        raise HTTPException(404, "Not ready")
    outputs = job.get("outputs", {})
    filename = outputs.get(kind)
    if not filename:
        raise HTTPException(404, f"No {kind} output")
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(404, "File missing")
    media = {
        "midi": "audio/midi",
        "musicxml": "application/vnd.recordare.musicxml+xml",
        "pdf": "application/pdf",
    }
    return FileResponse(path, media_type=media[kind], filename=path.name)
