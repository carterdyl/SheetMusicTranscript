# PianoTranscript

Convert solo piano audio recordings into sheet music (MIDI, MusicXML, PDF).

## Architecture

- **Backend** — FastAPI server handles uploads, serves job status and file downloads.
- **Worker** — RQ worker processes transcription jobs asynchronously.
- **Redis** — Job queue and metadata store.
- **Frontend** — React (Vite) SPA with file upload, progress polling, and download links.

### Transcription Model

Uses **[basic-pitch](https://github.com/spotify/basic-pitch)** by Spotify (Apache-2.0 license). It's a lightweight neural audio-to-MIDI model that works on CPU. No GPU required, though processing is slower on CPU.

## Quick Start

```bash
docker compose up --build
```

Then open **http://localhost:5173**.

1. Upload a `.wav` or `.mp3` file of solo piano.
2. Optionally set BPM and quantization.
3. Optionally choose a transposition (semitones). Default is **"Original (no transpose)"**, which keeps the output in the same key as the audio. Select a positive or negative semitone shift to transpose the output sheet music up or down before export.
4. Wait for processing (progress bar updates).
5. Download MIDI, MusicXML, or PDF.

## Outputs

Stored in `./data/outputs/` on the host (mounted into containers).

- `{job_id}.mid` — MIDI file
- `{job_id}.musicxml` — MusicXML (two staves: RH treble, LH bass)
- `{job_id}.pdf` — PDF (only if MuseScore is installed in the worker container)

## Configuration

See `.env.example`. Key variables:

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection |
| `DATA_DIR` | `/data` | Upload/output storage |
| `MAX_UPLOAD_BYTES` | `20971520` | 20 MB upload limit |
| `MUSESCORE_BIN` | `musescore4` | MuseScore CLI binary name |

## Limitations

- **Solo piano only** — not designed for full mixes or multi-instrument audio.
- Hand splitting uses a simple pitch threshold (default: MIDI 60 / middle C). Polyphonic voice separation is not implemented.
- Tempo estimation may be inaccurate for rubato or complex rhythms; provide BPM manually for best results.
- PDF rendering requires MuseScore CLI in the worker container (not included by default to keep image small).

## Swapping the Transcription Model

The transcription interface is in `backend/app/services/transcribe.py`. Replace the `transcribe()` function body — it must return `list[NoteEvent]` with fields `pitch`, `onset`, `offset`, `velocity`. The rest of the pipeline (quantization, export) is model-agnostic.

Candidate upgrades:
- **Onsets and Frames** (Magenta) — higher accuracy, needs TensorFlow + GPU
- **hft-transformer** — state-of-the-art, needs PyTorch + GPU

## Running Tests

```bash
cd backend
pip install -r requirements.txt pytest
pytest tests/
```
## Future Goals / Roadmap

- Mixed-audio support (piano reduction): Transcribe full mixes / multi-instrument audio by separating stems and generating a piano arrangement (not just note-for-note transcription).
- Multiple output versions: Offer alternative transcriptions (e.g., rhythm-simple vs rhythm-detailed, strict vs smooth quantization, different hand-splitting strategies).
- Difficulty-based arrangements: Generate beginner / intermediate / advanced piano arrangements from the same audio snippet (simplification, chord reduction, rhythmic simplification, range constraints).
- ~~Key transposition~~ — **Implemented.** Users can transpose the output by semitones before export.
