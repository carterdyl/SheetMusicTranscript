"""Load and normalise audio to mono 22050 Hz float32 numpy array."""
import numpy as np
import librosa


def load_audio(path: str, sr: int = 22050) -> tuple[np.ndarray, int]:
    y, sr_out = librosa.load(path, sr=sr, mono=True)
    return y, sr_out
