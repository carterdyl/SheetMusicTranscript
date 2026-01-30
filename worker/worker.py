"""RQ worker entrypoint + pipeline function."""
import json
import logging
import sys
import os

# Add backend to path so we can import app.*
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import OUTPUT_DIR
from app.storage.jobs import update_job
from app.services.transcribe import transcribe
from app.services.postprocess import estimate_tempo, quantize, split_hands
from app.services.export_midi import export_midi
from app.services.export_musicxml import export_musicxml
from app.services.render_pdf import render_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(params: dict):
    job_id = params["job_id"]
    audio_path = params["audio_path"]
    user_bpm = params.get("bpm", 0)
    quant = params.get("quantization", "1/16")
    split_point = params.get("split_point", 60)

    try:
        update_job(job_id, status="running", progress=5)

        # 1. Transcribe
        events = transcribe(audio_path)
        update_job(job_id, progress=50)

        if not events:
            raise RuntimeError("No notes detected in audio")

        # 2. Tempo
        fallback = user_bpm if user_bpm > 0 else 120
        bpm = estimate_tempo(audio_path, fallback_bpm=fallback) if user_bpm <= 0 else float(user_bpm)
        update_job(job_id, progress=60)

        # 3. Quantize
        events_q = quantize(events, bpm, quant)
        update_job(job_id, progress=65)

        # 4. Split hands
        rh, lh = split_hands(events_q, split_point)
        update_job(job_id, progress=70)

        # 5. Export MIDI
        midi_name = f"{job_id}.mid"
        export_midi(events_q, bpm, str(OUTPUT_DIR / midi_name))
        update_job(job_id, progress=80)

        # 6. Export MusicXML
        xml_name = f"{job_id}.musicxml"
        export_musicxml(rh, lh, bpm, str(OUTPUT_DIR / xml_name))
        update_job(job_id, progress=90)

        # 7. Render PDF (optional)
        pdf_name = f"{job_id}.pdf"
        pdf_ok = render_pdf(str(OUTPUT_DIR / xml_name), str(OUTPUT_DIR / pdf_name))
        update_job(job_id, progress=95)

        outputs = {"midi": midi_name, "musicxml": xml_name}
        if pdf_ok:
            outputs["pdf"] = pdf_name

        update_job(job_id, status="done", progress=100, outputs=json.dumps(outputs))
        logger.info("Job %s done", job_id)

    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        update_job(job_id, status="error", error=str(exc))


if __name__ == "__main__":
    from redis import Redis
    from rq import Worker, Queue
    from app.config import REDIS_URL

    conn = Redis.from_url(REDIS_URL)
    worker = Worker([Queue(connection=conn)], connection=conn)
    worker.work()
