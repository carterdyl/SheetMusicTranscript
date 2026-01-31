"""Unit tests for transpose_notes."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.transcribe import NoteEvent
from app.services.transpose import transpose_notes


def _make(pitches):
    return [NoteEvent(pitch=p, onset=i * 0.5, offset=i * 0.5 + 0.4, velocity=80) for i, p in enumerate(pitches)]


def test_basic_transpose_up():
    notes = _make([60, 64, 67])
    result = transpose_notes(notes, 2)
    assert [n.pitch for n in result] == [62, 66, 69]


def test_basic_transpose_down():
    notes = _make([60, 64, 67])
    result = transpose_notes(notes, -3)
    assert [n.pitch for n in result] == [57, 61, 64]


def test_zero_returns_identical():
    notes = _make([60, 64, 67])
    result = transpose_notes(notes, 0)
    assert result is notes  # same object, no copy


def test_clamp_high():
    notes = _make([105, 108])
    result = transpose_notes(notes, 5)
    assert [n.pitch for n in result] == [108, 108]


def test_clamp_low():
    notes = _make([23, 21])
    result = transpose_notes(notes, -5)
    assert [n.pitch for n in result] == [21, 21]


def test_timing_preserved():
    notes = _make([60])
    result = transpose_notes(notes, 7)
    assert result[0].onset == notes[0].onset
    assert result[0].offset == notes[0].offset
    assert result[0].velocity == notes[0].velocity
