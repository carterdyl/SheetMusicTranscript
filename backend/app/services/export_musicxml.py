"""Generate MusicXML with two staves (RH treble, LH bass) using music21."""
import logging
from music21 import stream, note, meter, tempo, clef, instrument
from app.services.transcribe import NoteEvent

logger = logging.getLogger(__name__)


def _events_to_part(events: list[NoteEvent], bpm: float, clef_obj, part_name: str) -> stream.Part:
    p = stream.Part()
    p.partName = part_name
    p.insert(0, clef_obj)
    p.insert(0, meter.TimeSignature("4/4"))
    p.insert(0, tempo.MetronomeMark(number=bpm))
    p.insert(0, instrument.Piano())

    for ev in events:
        n = note.Note(ev.pitch)
        n.quarterLength = max(0.25, (ev.offset - ev.onset) / (60.0 / bpm))
        n.volume.velocity = ev.velocity
        offset_ql = ev.onset / (60.0 / bpm)
        p.insert(offset_ql, n)

    p.makeMeasures(inPlace=True)
    return p


def export_musicxml(rh: list[NoteEvent], lh: list[NoteEvent], bpm: float, out_path: str):
    s = stream.Score()
    s.insert(0, _events_to_part(rh, bpm, clef.TrebleClef(), "Right Hand"))
    s.insert(0, _events_to_part(lh, bpm, clef.BassClef(), "Left Hand"))
    s.write("musicxml", fp=out_path)
    logger.info("Wrote MusicXML to %s", out_path)
