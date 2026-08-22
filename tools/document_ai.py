"""Script parser (Plain text, Fountain, and PDF with Document AI / pypdf fallback)."""
from __future__ import annotations

import os
from pathlib import Path


def parse_script(gcs_uri_or_path: str) -> dict:
    """Parse a script into raw text + page-anchored blocks.

    Accepts a gs:// URI or a local path (txt, fountain, pdf).
    Returns {"pages": [{"page_no": int, "text": str}]}.
    """
    path = Path(gcs_uri_or_path)

    # 1. Plain text / Fountain fast path ($0, no GCP needed)
    if not gcs_uri_or_path.startswith("gs://") and path.suffix.lower() in {".txt", ".fountain", ".md", ""}:
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            # Split scenes / rough pages by formfeed or double newline blocks
            chunks = [p.strip() for p in text.split("\n\n\n") if p.strip()] or [text]
            return {"pages": [{"page_no": i + 1, "text": c} for i, c in enumerate(chunks)]}

    # 2. Local PDF via pypdf fast path ($0, no GCP needed)
    if not gcs_uri_or_path.startswith("gs://") and path.suffix.lower() == ".pdf" and path.exists():
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            return {
                "pages": [
                    {"page_no": i + 1, "text": page.extract_text() or ""}
                    for i, page in enumerate(reader.pages)
                ]
            }
        except ImportError:
            pass

    # 3. Document AI route (if configured and installed)
    try:
        from google.cloud import documentai

        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us")
        processor_id = os.environ.get("DOCAI_PROCESSOR_ID", "")

        if project and processor_id:
            client = documentai.DocumentProcessorServiceClient()
            name = client.processor_path(project, location, processor_id)

            if gcs_uri_or_path.startswith("gs://"):
                raw = documentai.RawDocument(
                    gcs_uri=gcs_uri_or_path, mime_type="application/pdf"
                )
            else:
                content = Path(gcs_uri_or_path).read_bytes()
                raw = documentai.RawDocument(content=content, mime_type="application/pdf")

            req = documentai.ProcessRequest(name=name, raw_document=raw)
            doc = client.process_document(request=req).document
            return {
                "pages": [
                    {
                        "page_no": i + 1,
                        "text": doc.text[
                            p.layout.text_anchor.text_segments[0].start_index : p.layout.text_anchor.text_segments[0].end_index
                        ],
                    }
                    for i, p in enumerate(doc.pages)
                ]
            }
    except Exception:
        pass

    # Default fallback
    if Path(gcs_uri_or_path).exists():
        text = Path(gcs_uri_or_path).read_text(encoding="utf-8", errors="ignore")
        return {"pages": [{"page_no": 1, "text": text}]}

    return {"pages": [{"page_no": 1, "text": str(gcs_uri_or_path)}]}

