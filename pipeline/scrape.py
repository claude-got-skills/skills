"""Content extraction for Anthropic documentation sources.

Extraction strategies by page type:
- api-docs (platform.claude.com): trafilatura primary, Jina Reader fallback
- support (support.claude.com): Jina Reader only (JS-rendered via Intercom)
- github: Raw content URL (raw.githubusercontent.com) for pure markdown
- claude-code (code.claude.com): Jina Reader only (Next.js, JS-rendered)
"""

import logging
import os
import re
import unicodedata
from urllib.parse import urlparse

import requests
import trafilatura

from .config import get_jina_headers

logger = logging.getLogger(__name__)

# Request timeout in seconds
REQUEST_TIMEOUT = 30


# ── Content Normalization ────────────────────────────────────────────────────

def normalize_content(text: str) -> str:
    """Normalize extracted content to prevent false-positive diffs.

    Applies:
    - Unicode normalization (NFC)
    - Collapse multiple blank lines to single blank line
    - Strip trailing whitespace from each line
    - Strip leading/trailing whitespace from the whole text
    - Remove common dynamic elements (timestamps, session IDs)
    """
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)

    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.splitlines()]

    # Collapse multiple consecutive blank lines into one
    normalized_lines = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        normalized_lines.append(line)
        prev_blank = is_blank

    text = "\n".join(normalized_lines)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove common dynamic elements that cause false diffs
    # e.g., "Last updated: Mar 7, 2026" or similar date stamps
    text = re.sub(
        r"(?:Last updated|Updated|Modified):?\s*\w+\s+\d{1,2},?\s*\d{4}",
        "",
        text,
    )

    return text


# ── GitHub Raw Content ───────────────────────────────────────────────────────

def _github_to_raw_url(url: str) -> str:
    """Convert a GitHub blob URL to a raw.githubusercontent.com URL.

    Example:
        github.com/anthropics/claude-code/blob/main/CHANGELOG.md
        -> raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
    """
    parsed = urlparse(url)
    path = parsed.path
    # /anthropics/claude-code/blob/main/CHANGELOG.md
    # -> /anthropics/claude-code/main/CHANGELOG.md
    path = path.replace("/blob/", "/", 1)
    return f"https://raw.githubusercontent.com{path}"


def extract_github(url: str) -> str | None:
    """Extract content from a GitHub file via raw URL."""
    raw_url = _github_to_raw_url(url)
    try:
        resp = requests.get(raw_url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        content = resp.text
        if content and len(content) > 50:
            return normalize_content(content)
        logger.warning("GitHub content too short for %s", url)
        return None
    except requests.RequestException as e:
        logger.error("GitHub extraction failed for %s: %s", url, e)
        return None


# ── Trafilatura Extraction ───────────────────────────────────────────────────

def extract_with_trafilatura(url: str) -> str | None:
    """Extract content using trafilatura (server-rendered pages)."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning("Trafilatura could not fetch %s", url)
            return None

        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
        )

        if not content or len(content) < 50:
            logger.warning("Trafilatura extracted insufficient content from %s", url)
            return None

        return normalize_content(content)

    except (requests.RequestException, OSError, ValueError, AttributeError) as e:
        logger.warning("Trafilatura failed for %s: %s", url, e)
        return None


# ── Jina Reader Extraction ───────────────────────────────────────────────────

def extract_with_jina(url: str) -> str | None:
    """Extract content using Jina Reader (JS-rendered pages)."""
    jina_url = f"https://r.jina.ai/{url}"
    headers = get_jina_headers()

    try:
        resp = requests.get(jina_url, timeout=REQUEST_TIMEOUT, headers=headers)
        resp.raise_for_status()

        text = resp.text
        if not text or len(text) < 50:
            logger.warning("Jina Reader returned insufficient content for %s", url)
            return None

        return normalize_content(text)

    except requests.RequestException as e:
        logger.warning("Jina Reader failed for %s: %s", url, e)
        return None


# ── Main Extraction Entry Point ──────────────────────────────────────────────

def extract_content(url: str, page_type: str) -> tuple[str | None, str]:
    """Extract content from a URL using the appropriate strategy.

    Args:
        url: The source URL to scrape.
        page_type: One of 'api-docs', 'support', 'github', 'claude-code'.

    Returns:
        Tuple of (content, extraction_method). Content is None on failure.
    """
    if page_type == "github":
        content = extract_github(url)
        return content, "github_raw"

    if page_type == "support":
        # JS-rendered (Intercom) — Jina only
        content = extract_with_jina(url)
        return content, "jina_reader"

    if page_type == "claude-code":
        # Next.js, JS-rendered — Jina only
        content = extract_with_jina(url)
        return content, "jina_reader"

    if page_type == "api-docs":
        # Server-rendered — trafilatura primary, Jina fallback
        content = extract_with_trafilatura(url)
        if content:
            return content, "trafilatura"

        logger.info("Falling back to Jina Reader for %s", url)
        content = extract_with_jina(url)
        return content, "jina_reader"

    logger.error("Unknown page type '%s' for %s", page_type, url)
    return None, "unknown"
