"""Script parser (plain text, Fountain, PDF with local pypdf / Document AI)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

_TEXT_EXTS = {".txt", ".fountain", ".md", ""}


def _parse_text_pages(text: str) -> dict:
    chunks = [p.strip() for p in text.split("\n\n\n") if p.strip()] or [text]
    return {"pages": [{"page_no": i + 1, "text": c} for i, c in enumerate(chunks)]}


def _parse_local_pdf(path: Path) -> dict | None:
    try:
        import pypdf
    except ImportError:
        log.warning("pypdf not installed; skipping local PDF fast-path")
        return None
    try:
        reader = pypdf.PdfReader(str(path))
    except Exception as e:
        log.error("pypdf failed on %s: %s", path, e)
        return None
    return {
        "pages": [
            {"page_no": i + 1, "text": page.extract_text() or ""}
            for i, page in enumerate(reader.pages)
        ]
    }


def _parse_via_document_ai(source: str) -> dict | None:
    """Parse via Document AI. Uses inline bytes for local paths, GcsDocument
    for gs:// URIs. Returns None if Document AI isn't configured; raises on
    real failures so the caller can log them explicitly."""
    try:
        from google.cloud import documentai
    except ImportError:
        log.warning("google-cloud-documentai not installed")
        return None

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us")
    processor_id = os.environ.get("DOCAI_PROCESSOR_ID", "")
    if not (project and processor_id):
        log.info("Document AI not configured (need DOCAI_PROCESSOR_ID); skipping")
        return None

    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(project, location, processor_id)

    if source.startswith("gs://"):
        req = documentai.ProcessRequest(
            name=name,
            gcs_document=documentai.GcsDocument(
                gcs_uri=source, mime_type="application/pdf"
            ),
        )
    else:
        content = Path(source).read_bytes()
        req = documentai.ProcessRequest(
            name=name,
            raw_document=documentai.RawDocument(
                content=content, mime_type="application/pdf"
            ),
        )
    doc = client.process_document(request=req).document
    return {
        "pages": [
            {
                "page_no": i + 1,
                "text": doc.text[
                    p.layout.text_anchor.text_segments[0].start_index
                    : p.layout.text_anchor.text_segments[0].end_index
                ],
            }
            for i, p in enumerate(doc.pages)
        ]
    }


def parse_script(gcs_uri_or_path: str) -> dict:
    """Parse a script into raw text + page-anchored blocks.

    Accepts a gs:// URI or a local path (txt, fountain, pdf).
    Returns {"pages": [{"page_no": int, "text": str}]}.
    """
    is_gcs = gcs_uri_or_path.startswith("gs://")
    path = None if is_gcs else Path(gcs_uri_or_path)

    if not is_gcs and path and path.exists() and path.suffix.lower() in _TEXT_EXTS:
        return _parse_text_pages(path.read_text(encoding="utf-8"))

    if not is_gcs and path and path.exists() and path.suffix.lower() == ".pdf":
        via_pypdf = _parse_local_pdf(path)
        if via_pypdf is not None:
            return via_pypdf

    via_docai = _parse_via_document_ai(gcs_uri_or_path)
    if via_docai is not None:
        return via_docai

    if not is_gcs and path and path.exists():
        return {"pages": [{"page_no": 1, "text": path.read_text(encoding="utf-8")}]}

    raise FileNotFoundError(
        f"parse_script: cannot resolve {gcs_uri_or_path!r} — file missing "
        "and Document AI unavailable"
    )
