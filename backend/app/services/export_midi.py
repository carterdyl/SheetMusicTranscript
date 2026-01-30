"""Export note events to a MIDI file using pretty_midi."""
import logging
import pretty_midi
from app.services.transcribe import NoteEvent

logger = logging.getLogger(__name__)


def export_midi(events: list[NoteEvent], bpm: float, out_path: str):
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst = pretty_midi.Instrument(program=0, name="Piano")
    for e in events:
        inst.notes.append(pretty_midi.Note(
            velocity=e.velocity, pitch=e.pitch, start=e.onset, end=e.offset,
        ))
    pm.instruments.append(inst)
    pm.write(out_path)
    logger.info("Wrote MIDI to %s", out_path)
