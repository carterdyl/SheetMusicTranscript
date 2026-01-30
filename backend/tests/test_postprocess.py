import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.postprocess import quantize, split_hands
from app.services.transcribe import NoteEvent


def test_quantize_snaps_to_grid():
    bpm = 120.0
    grid = 60.0 / 120.0 * (4 * 1 / 16)  # = 0.125 s
    events = [NoteEvent(pitch=60, onset=0.06, offset=0.19, velocity=80)]
    result = quantize(events, bpm, "1/16")
    assert result[0].onset == 0.0  # snaps to 0
    assert result[0].offset == round(0.19 / grid) * grid


def test_quantize_min_duration():
    bpm = 120.0
    events = [NoteEvent(pitch=60, onset=0.0, offset=0.01, velocity=80)]
    result = quantize(events, bpm, "1/16")
    assert result[0].offset > result[0].onset


def test_split_hands():
    events = [
        NoteEvent(pitch=72, onset=0, offset=1, velocity=80),
        NoteEvent(pitch=48, onset=0, offset=1, velocity=60),
        NoteEvent(pitch=60, onset=0, offset=1, velocity=70),
    ]
    rh, lh = split_hands(events, 60)
    assert len(rh) == 2  # 72 and 60 (>=60)
    assert len(lh) == 1  # 48
    assert all(e.pitch >= 60 for e in rh)
    assert all(e.pitch < 60 for e in lh)
