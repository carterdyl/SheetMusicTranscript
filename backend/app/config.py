import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 20 * 1024 * 1024))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MUSESCORE_BIN = os.getenv("MUSESCORE_BIN", "musescore4")

for d in (UPLOAD_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)
