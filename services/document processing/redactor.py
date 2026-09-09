"""Real PDF redaction using PyMuPDF's redaction annotations.

CRITICAL: apply_redactions() actually removes the underlying text/graphics
content beneath the annotation, unlike simply drawing a black rectangle over
the page. After redaction we reopen the saved file and re-extract its text to
verify that none of the original raw sensitive values survive. If the
verification fails, the caller must NOT release the file - this module raises
so the pipeline fails closed.
"""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


class RedactionVerificationError(Exception):
    """Raised when a sanitized PDF still contains a raw sensitive value."""


def redact_pdf(doc: fitz.Document, detections: list[dict]) -> int:
    """Apply redactions in-place on an already-open fitz.Document.

    detections: list of {"page": int, "bbox": [x0,y0,x1,y1]}
    Returns the number of redaction boxes applied.
    """
    by_page: dict[int, list[list[float]]] = {}
    for d in detections:
        if not d.get("bbox"):
            continue
        by_page.setdefault(d["page"], []).append(d["bbox"])

    applied = 0
    for page_number, boxes in by_page.items():
        if page_number >= doc.page_count:
            continue
        page = doc[page_number]
        for bbox in boxes:
            rect = fitz.Rect(*bbox)
            rect.x0 -= 1.5
            rect.y0 -= 1.5
            rect.x1 += 1.5
            rect.y1 += 1.5
            page.add_redact_annot(rect, fill=(0, 0, 0))
            applied += 1
        if boxes:
            page.apply_redactions()
    return applied


def verify_no_raw_values(sanitized_path: str, raw_values: list[str]) -> list[str]:
    """Reopens the sanitized PDF and checks that none of the raw sensitive
    values are still extractable. Returns a list of values that leaked (empty
    list means verification passed)."""
    leaked: list[str] = []
    doc = fitz.open(sanitized_path)
    try:
        full_text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()

    for value in raw_values:
        v = value.strip()
        if len(v) < 3:
            continue
        if v in full_text:
            leaked.append(v)
    return leaked


def assert_redaction_clean(sanitized_path: str, raw_values: list[str]) -> None:
    leaked = verify_no_raw_values(sanitized_path, raw_values)
    if leaked:
        try:
            Path(sanitized_path).unlink(missing_ok=True)
        except OSError:
            pass
        raise RedactionVerificationError(
            f"Redaction verification failed: {len(leaked)} sensitive value(s) still extractable from output PDF"
        )
