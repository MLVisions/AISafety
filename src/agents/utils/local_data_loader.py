"""
Local data loader — reads files from src/agents/local_data/ for LLM context.

Supported formats:
  - PDF:  sent as base64 document attachment (native support in modern LLMs)
  - PNG/JPG/GIF/WebP: sent as base64 image attachment
  - PPTX/DOCX: logged as unsupported (export to PDF)
"""

import base64
import logging
import mimetypes
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

LOCAL_DATA_DIR = Path(__file__).parent.parent / "local_data"

# Formats natively supported by modern LLM providers via litellm
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
_DOCUMENT_EXTENSIONS = {".pdf"}
_UNSUPPORTED_EXTENSIONS = {".pptx", ".docx", ".xlsx"}


@dataclass
class LocalAttachment:
    """A file ready to be sent to an LLM as a multimodal content block."""

    kind: str  # "image" or "document"
    mime: str
    data: str  # base64-encoded
    filename: str


def load_local_files(filenames: list[str]) -> list[LocalAttachment]:
    """Load and encode files from local_data/ for LLM consumption.

    Args:
        filenames: List of filenames (relative to local_data/).

    Returns:
        List of LocalAttachment objects for supported file types.
        Unsupported files are logged and skipped.
    """
    attachments: list[LocalAttachment] = []

    for name in filenames:
        path = LOCAL_DATA_DIR / name
        if not path.is_file():
            logger.warning("Local data file not found: %s", path)
            continue

        ext = path.suffix.lower()

        if ext in _UNSUPPORTED_EXTENSIONS:
            logger.warning(
                "Unsupported file type '%s' for %s. Export to PDF for LLM support.",
                ext,
                name,
            )
            continue

        if ext in _IMAGE_EXTENSIONS:
            mime = mimetypes.guess_type(str(path))[0] or "image/png"
            data = base64.b64encode(path.read_bytes()).decode()
            attachments.append(LocalAttachment("image", mime, data, name))
            logger.debug("Loaded local image: %s (%d bytes)", name, path.stat().st_size)

        elif ext in _DOCUMENT_EXTENSIONS:
            mime = "application/pdf"
            data = base64.b64encode(path.read_bytes()).decode()
            attachments.append(LocalAttachment("document", mime, data, name))
            logger.debug("Loaded local document: %s (%d bytes)", name, path.stat().st_size)

        else:
            logger.warning("Unknown file type '%s' for %s, skipping.", ext, name)

    return attachments
