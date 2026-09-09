"""Regex + keyword based sensitive-data detection.

No machine learning. Every detection is produced deterministically from a
regex pattern or a keyword dictionary entry loaded by the caller (typically
sourced from the database, seeded from config/patterns.json and
config/keywords.json).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from extractor import ExtractionResult, bbox_for_span


@dataclass
class PatternRule:
    name: str
    category: str
    pattern: str
    priority: int = 50
    requires_keyword_context: bool = False
    context_keywords: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class Detection:
    category: str
    page: int
    bbox: tuple[float, float, float, float] | None
    value: str  # raw matched text - kept only in-memory for this request
    source: str  # "regex" or "keyword"
    rule_name: str


def _luhn_valid(digits: str) -> bool:
    digits = re.sub(r"\D", "", digits)
    if len(digits) < 12:
        return False
    total = 0
    reverse = digits[::-1]
    for i, ch in enumerate(reverse):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


# (prefix_range_start, prefix_range_end, digit_length) per major card network.
# A match must fall in one of these IIN/BIN ranges in addition to passing Luhn -
# this is the same two-factor check real card scanners use, and meaningfully
# cuts false positives versus Luhn alone (roughly 1 in 10 random numbers is
# Luhn-valid by chance).
_CARD_NETWORK_RANGES: list[tuple[int, int, set[int]]] = [
    (4000, 4999, {13, 16, 19}),  # Visa
    (5100, 5599, {16}),  # Mastercard (legacy range)
    (2221, 2720, {16}),  # Mastercard (2017+ range)
    (3400, 3499, {15}),  # Amex
    (3700, 3799, {15}),  # Amex
    (6011, 6011, {16, 19}),  # Discover
    (6440, 6499, {16, 19}),  # Discover
    (6500, 6599, {16, 19}),  # Discover
    (3000, 3059, {14}),  # Diners Club
    (3600, 3699, {14}),  # Diners Club
    (3800, 3899, {14}),  # Diners Club
    (3528, 3589, {16}),  # JCB
]


def _card_network_valid(digits: str) -> bool:
    digits = re.sub(r"\D", "", digits)
    if not digits:
        return False
    prefix4 = int(digits[:4]) if len(digits) >= 4 else -1
    length = len(digits)
    return any(lo <= prefix4 <= hi and length in lengths for lo, hi, lengths in _CARD_NETWORK_RANGES)


def _nic_new_format_plausible(value: str) -> bool:
    """The new-format Sri Lankan NIC encodes a 2-digit birth year followed by
    a 3-digit day-of-year (1-366 for men, 501-866 for women). A bare 12-digit
    number that can't possibly be a valid date-of-birth encoding is almost
    certainly something else (an account number, a serial, ...), so this
    rejects it rather than flag a false positive."""
    digits = re.sub(r"\D", "", value)
    if len(digits) != 12:
        return False
    day_component = int(digits[2:5])
    return 1 <= day_component <= 366 or 501 <= day_component <= 866


class ClaimedRanges:
    """Tracks already-claimed character ranges per page so higher-priority
    patterns win overlapping matches (e.g. a card number should not also be
    reported as a bank account and a bare NIC)."""

    def __init__(self) -> None:
        self._ranges: dict[int, list[tuple[int, int, int]]] = {}

    def is_claimed(self, page: int, start: int, end: int) -> bool:
        for cs, ce, _prio in self._ranges.get(page, []):
            if not (end <= cs or start >= ce):
                return True
        return False

    def claim(self, page: int, start: int, end: int, priority: int) -> None:
        self._ranges.setdefault(page, []).append((start, end, priority))


def _line_containing(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end]


def detect(
    extraction: ExtractionResult,
    rules: list[PatternRule],
    keywords: dict[str, list[str]],
) -> list[Detection]:
    detections: list[Detection] = []
    claimed = ClaimedRanges()

    ordered_rules = sorted([r for r in rules if r.enabled], key=lambda r: -r.priority)

    for page_index in extraction.pages:
        text = page_index.text
        if not text.strip():
            continue

        for rule in ordered_rules:
            try:
                compiled = re.compile(rule.pattern)
            except re.error:
                continue

            for m in compiled.finditer(text):
                start, end = m.start(), m.end()
                if claimed.is_claimed(page_index.page, start, end):
                    continue

                matched_text = m.group(0)

                if rule.category == "card" and not (_luhn_valid(matched_text) and _card_network_valid(matched_text)):
                    continue

                if rule.name == "new_nic" and not _nic_new_format_plausible(matched_text):
                    continue

                if rule.requires_keyword_context:
                    line = _line_containing(text, start).lower()
                    if not any(kw.lower() in line for kw in rule.context_keywords):
                        continue

                bbox = bbox_for_span(page_index, start, end)
                claimed.claim(page_index.page, start, end, rule.priority)
                detections.append(
                    Detection(
                        category=rule.category,
                        page=page_index.page,
                        bbox=bbox,
                        value=matched_text.strip(),
                        source="regex",
                        rule_name=rule.name,
                    )
                )

        # Keyword dictionary pass (phrase search, case-insensitive)
        lowered = text.lower()
        for category, terms in keywords.items():
            for term in terms:
                term_l = term.lower().strip()
                if not term_l:
                    continue
                search_from = 0
                while True:
                    idx = lowered.find(term_l, search_from)
                    if idx == -1:
                        break
                    start, end = idx, idx + len(term_l)
                    search_from = end
                    if claimed.is_claimed(page_index.page, start, end):
                        continue
                    bbox = bbox_for_span(page_index, start, end)
                    claimed.claim(page_index.page, start, end, 10)
                    detections.append(
                        Detection(
                            category=category,
                            page=page_index.page,
                            bbox=bbox,
                            value=text[start:end],
                            source="keyword",
                            rule_name=term,
                        )
                    )

    return detections


def summarize_categories(detections: list[Detection]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for d in detections:
        counts[d.category] = counts.get(d.category, 0) + 1
    return counts
