"""Deterministic readability-style HTML extractor for Bucket 02.

The goal is modest and auditable: strip site chrome, keep the main public
content, and emit clean text blocks the dossier extractor can consume.
This is not a full Mozilla Readability port; it is a lightweight,
fixture-friendly heuristic tuned for wildlife-center sites.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable


NEGATIVE_HINTS = (
    "nav",
    "menu",
    "footer",
    "header",
    "sidebar",
    "share",
    "social",
    "cookie",
    "popup",
    "promo",
    "breadcrumb",
    "alert",
    "banner",
)

POSITIVE_HINTS = (
    "main",
    "content",
    "article",
    "post",
    "entry",
    "page",
    "about",
    "mission",
    "contact",
    "help",
    "wildlife",
)

BLOCK_TAGS = {
    "address",
    "article",
    "blockquote",
    "br",
    "div",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "p",
    "section",
    "tr",
}

SKIP_TAGS = {"script", "style", "noscript", "svg", "canvas", "template"}

TAG_CANDIDATE_RE = re.compile(
    r"<(?P<tag>main|article|section|div|body)\b(?P<attrs>[^>]*)>(?P<html>.*?)</(?P=tag)>",
    re.IGNORECASE | re.DOTALL,
)

TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass
class ReadabilityExtract:
    title: str
    text: str
    score: int
    paragraph_count: int


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        t = tag.lower()
        if t in SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if t == "li":
            self._parts.append("\n- ")
        elif t in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if t in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth or not data:
            return
        self._parts.append(data)

    def text(self) -> str:
        blob = html.unescape("".join(self._parts))
        lines = []
        for raw in blob.splitlines():
            line = re.sub(r"\s+", " ", raw).strip()
            if line:
                lines.append(line)
        return "\n\n".join(lines)


def extract_main_content(html_text: str, *, fallback_title: str = "") -> ReadabilityExtract:
    """Pick the most article-like fragment from a page and textify it."""
    if not html_text:
        return ReadabilityExtract(title=fallback_title, text="", score=0, paragraph_count=0)

    cleaned = _drop_irrelevant_blocks(html_text)
    title = _extract_title(cleaned) or fallback_title
    for tag in ("main", "article"):
        fragment = _first_tag_fragment(cleaned, tag)
        if not fragment:
            continue
        text = _html_to_text(fragment)
        if len(text.split()) >= 20:
            score = len(text) + 250
            return ReadabilityExtract(
                title=title,
                text=text,
                score=score,
                paragraph_count=_paragraph_count(text),
            )
    candidates = list(_candidate_fragments(cleaned))
    if not candidates:
        text = _html_to_text(cleaned)
        return ReadabilityExtract(
            title=title,
            text=text,
            score=len(text),
            paragraph_count=_paragraph_count(text),
        )

    best_score, best_text = max(candidates, key=lambda item: item[0])
    return ReadabilityExtract(
        title=title,
        text=best_text,
        score=best_score,
        paragraph_count=_paragraph_count(best_text),
    )


def _drop_irrelevant_blocks(html_text: str) -> str:
    cleaned = html_text
    for tag in SKIP_TAGS:
        cleaned = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}>",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return cleaned


def _extract_title(html_text: str) -> str:
    match = TITLE_RE.search(html_text or "")
    if not match:
        return ""
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()


def _first_tag_fragment(html_text: str, tag: str) -> str:
    match = re.search(
        rf"<{tag}\b[^>]*>(.*?)</{tag}>",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _candidate_fragments(html_text: str) -> Iterable[tuple[int, str]]:
    for match in TAG_CANDIDATE_RE.finditer(html_text):
        tag = (match.group("tag") or "").lower()
        attrs = (match.group("attrs") or "").lower()
        fragment = match.group("html") or ""
        text = _html_to_text(fragment)
        if len(text.split()) < 20:
            continue
        score = len(text)
        if tag == "body":
            score -= 400
        score += 180 * sum(1 for hint in POSITIVE_HINTS if hint in attrs)
        score -= 220 * sum(1 for hint in NEGATIVE_HINTS if hint in attrs)
        score += 45 * len(re.findall(r"<h[1-6]\b", fragment, flags=re.IGNORECASE))
        score += 12 * text.count("\n\n")
        score -= 18 * len(re.findall(r"<a\b", fragment, flags=re.IGNORECASE))
        yield (score, text)


def _html_to_text(fragment: str) -> str:
    parser = _TextExtractor()
    parser.feed(fragment or "")
    return parser.text()


def _paragraph_count(text: str) -> int:
    if not text:
        return 0
    return len([block for block in text.split("\n\n") if block.strip()])
