"""Render MusicXML to PDF via MuseScore CLI (optional)."""
import logging
import shutil
import subprocess
from pathlib import Path
from app.config import MUSESCORE_BIN

logger = logging.getLogger(__name__)


def render_pdf(musicxml_path: str, pdf_path: str) -> bool:
    exe = shutil.which(MUSESCORE_BIN) or shutil.which("mscore") or shutil.which("musescore")
    if not exe:
        logger.warning("MuseScore not found; skipping PDF render")
        return False
    try:
        subprocess.run(
            [exe, "-o", pdf_path, musicxml_path],
            check=True, timeout=120, capture_output=True,
        )
        logger.info("Rendered PDF to %s", pdf_path)
        return True
    except Exception as exc:
        logger.warning("PDF render failed: %s", exc)
        return False
