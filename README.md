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
3. Wait for processing (progress bar updates).
4. Download MIDI, MusicXML, or PDF.

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
