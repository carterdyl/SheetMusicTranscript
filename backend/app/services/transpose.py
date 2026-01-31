"""Symbolic transposition of note events by semitone shift.

Notes shifted outside the piano range (min_pitch..max_pitch) are clamped
to the nearest boundary.  Timing and velocity are preserved.
"""
from app.services.transcribe import NoteEvent


def transpose_notes(
    notes: list[NoteEvent],
    semitones: int,
    min_pitch: int = 21,
    max_pitch: int = 108,
) -> list[NoteEvent]:
    """Return a new list of NoteEvents with pitches shifted by *semitones*.

    Strategy for out-of-range notes: **clamp** to *min_pitch* / *max_pitch*.
    Timing (onset/offset) and velocity are unchanged.

    If *semitones* is 0 the original list is returned as-is (no copy).
    """
    if semitones == 0:
        return notes

    out: list[NoteEvent] = []
    for n in notes:
        new_pitch = n.pitch + semitones
        new_pitch = max(min_pitch, min(max_pitch, new_pitch))
        out.append(NoteEvent(
            pitch=new_pitch,
            onset=n.onset,
            offset=n.offset,
            velocity=n.velocity,
        ))
    return out
