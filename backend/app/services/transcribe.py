"""Piano transcription using Spotify basic-pitch (Apache-2.0).

basic-pitch is a lightweight neural piano/instrument transcription model
that runs well on CPU.  It outputs MIDI-like note events.
"""
import logging
from dataclasses import dataclass

import numpy as np
from basic_pitch.inference import predict

logger = logging.getLogger(__name__)


@dataclass
class NoteEvent:
    pitch: int      # MIDI note number 0-127
    onset: float    # seconds
    offset: float   # seconds
    velocity: int   # 1-127


def transcribe(audio_path: str) -> list[NoteEvent]:
    """Run basic-pitch on *audio_path* and return note events."""
    logger.info("Running basic-pitch on %s", audio_path)
    model_output, midi_data, note_events = predict(audio_path)

    events: list[NoteEvent] = []
    for onset, offset, pitch, vel, *_ in note_events:
        events.append(NoteEvent(
            pitch=int(pitch),
            onset=float(onset),
            offset=float(offset),
            velocity=max(1, min(127, int(vel * 127))),
        ))
    events.sort(key=lambda e: (e.onset, e.pitch))
    logger.info("Transcribed %d notes", len(events))
    return events
