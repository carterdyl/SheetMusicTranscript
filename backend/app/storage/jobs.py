"""Thin job metadata layer backed by Redis hashes."""
import json
from redis import Redis
from app.config import REDIS_URL

_redis = None

def _r() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis

def _key(job_id: str) -> str:
    return f"job:{job_id}"

def create_job(job_id: str, params: dict):
    _r().hset(_key(job_id), mapping={
        "status": "queued",
        "progress": "0",
        "params": json.dumps(params),
    })

def update_job(job_id: str, **fields):
    _r().hset(_key(job_id), mapping={str(k): str(v) for k, v in fields.items()})

def get_job(job_id: str) -> dict | None:
    data = _r().hgetall(_key(job_id))
    if not data:
        return None
    data["progress"] = int(data.get("progress", 0))
    if "outputs" in data:
        data["outputs"] = json.loads(data["outputs"])
    if "params" in data:
        data["params"] = json.loads(data["params"])
    return data
