"""Maps a risk score onto a security classification using configurable
thresholds. Fails closed: a score above every configured range is treated as
the most severe configured classification rather than silently passing."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClassificationThreshold:
    classification: str
    min_score: int
    max_score: int


def classify(score: int, thresholds: list[ClassificationThreshold]) -> str:
    ordered = sorted(thresholds, key=lambda t: t.min_score)
    for t in ordered:
        if t.min_score <= score <= t.max_score:
            return t.classification
    if ordered and score > ordered[-1].max_score:
        return ordered[-1].classification
    if ordered and score < ordered[0].min_score:
        return ordered[0].classification
    return "RESTRICTED"
