"""Document AI script parser (PDF / Fountain / plain text)."""
from __future__ import annotations

import os
from pathlib import Path

from google.cloud import documentai


def parse_script(gcs_uri_or_path: str) -> dict:
    """Parse a script into raw text + page-anchored blocks.

    Accepts a gs:// URI or a local path. Returns
    {"pages": [{"page_no": int, "text": str}]}.
    """
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us")
    processor_id = os.environ["DOCAI_PROCESSOR_ID"]

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
            {"page_no": i + 1, "text": doc.text[p.layout.text_anchor.text_segments[0].start_index
                                                : p.layout.text_anchor.text_segments[0].end_index]}
            for i, p in enumerate(doc.pages)
        ]
    }
