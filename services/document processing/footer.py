"""Applies a classification footer to every page, e.g.
"RESTRICTED | SECUREPRINT PROTECTED | SP-18EFDD01"."""
from __future__ import annotations

import fitz  # PyMuPDF


def build_footer_text(classification: str, job_id: str, organisation: str, timestamp: str) -> str:
    return f"{classification} | {organisation} PROTECTED | {job_id} | {timestamp}"


def apply_footer(doc: fitz.Document, footer_text: str, font_size: int = 8) -> None:
    for page in doc:
        rect = page.rect
        footer_rect = fitz.Rect(24, rect.height - 26, rect.width - 24, rect.height - 10)
        page.insert_textbox(
            footer_rect,
            footer_text,
            fontsize=font_size,
            fontname="helv",
            color=(0.15, 0.15, 0.15),
            align=fitz.TEXT_ALIGN_CENTER,
        )
