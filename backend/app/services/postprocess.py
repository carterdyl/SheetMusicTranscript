"""Tempo estimation, quantization, and hand splitting."""
import logging
import numpy as np
import librosa
from app.services.transcribe import NoteEvent

logger = logging.getLogger(__name__)


def estimate_tempo(audio_path: str, fallback_bpm: int = 120) -> float:
    try:
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(np.atleast_1d(tempo)[0])
        if bpm < 30 or bpm > 300:
            raise ValueError(f"Unreasonable tempo {bpm}")
        logger.info("Estimated tempo: %.1f BPM", bpm)
        return bpm
    except Exception:
        logger.warning("Tempo estimation failed, using fallback %d", fallback_bpm)
        return float(fallback_bpm)


def quantize(events: list[NoteEvent], bpm: float, quantization: str = "1/16") -> list[NoteEvent]:
    num, denom = (int(x) for x in quantization.split("/"))
    grid_dur = 60.0 / bpm * (4 * num / denom)  # duration of one grid unit in seconds
    min_dur = grid_dur  # minimum note duration = 1 grid unit

    quantized: list[NoteEvent] = []
    for e in events:
        onset_q = round(e.onset / grid_dur) * grid_dur
        offset_q = round(e.offset / grid_dur) * grid_dur
        if offset_q <= onset_q:
            offset_q = onset_q + min_dur
        quantized.append(NoteEvent(
            pitch=e.pitch, onset=onset_q, offset=offset_q, velocity=e.velocity,
        ))
    return quantized


def split_hands(events: list[NoteEvent], split_point: int = 60) -> tuple[list[NoteEvent], list[NoteEvent]]:
    rh = [e for e in events if e.pitch >= split_point]
    lh = [e for e in events if e.pitch < split_point]
    return rh, lh
