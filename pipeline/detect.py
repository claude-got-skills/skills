"""SHA-256 change detection with checkpoint.json persistence."""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import CHECKPOINT_FILE

logger = logging.getLogger(__name__)


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_checkpoint() -> dict[str, Any]:
    """Load the checkpoint file. Returns empty dict if missing or corrupt."""
    if not CHECKPOINT_FILE.exists():
        logger.info("No checkpoint file found — first run")
        return {}

    try:
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
        logger.info("Loaded checkpoint with %d entries", len(data.get("sources", {})))
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load checkpoint: %s", e)
        return {}


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    """Save the checkpoint file atomically (write to tmp then rename)."""
    checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()

    tmp_path = CHECKPOINT_FILE.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            json.dump(checkpoint, f, indent=2)
        tmp_path.rename(CHECKPOINT_FILE)
        logger.info("Checkpoint saved with %d entries", len(checkpoint.get("sources", {})))
    except OSError as e:
        logger.error("Failed to save checkpoint: %s", e)
        # Clean up temp file if rename failed
        if tmp_path.exists():
            tmp_path.unlink()


def detect_change(
    url: str,
    content: str,
    checkpoint: dict[str, Any],
) -> tuple[bool, str, str | None]:
    """Check if content has changed since last checkpoint.

    Args:
        url: The source URL (used as key).
        content: The current content to check.
        checkpoint: The loaded checkpoint data.

    Returns:
        Tuple of (has_changed, new_hash, old_hash).
        old_hash is None if this is a new source.
    """
    new_hash = compute_hash(content)

    sources = checkpoint.get("sources", {})
    entry = sources.get(url)

    if entry is None:
        logger.info("New source (no previous hash): %s", url)
        return True, new_hash, None

    old_hash = entry.get("hash", "")
    if new_hash != old_hash:
        logger.info("Change detected: %s", url)
        return True, new_hash, old_hash

    logger.debug("No change: %s", url)
    return False, new_hash, old_hash


def update_checkpoint_entry(
    checkpoint: dict[str, Any],
    url: str,
    content_hash: str,
    content: str,
    extraction_method: str,
) -> None:
    """Update a single source entry in the checkpoint.

    Stores the content for future diff generation.
    """
    if "sources" not in checkpoint:
        checkpoint["sources"] = {}

    now = datetime.now(timezone.utc).isoformat()

    entry = checkpoint["sources"].get(url, {})
    entry.update({
        "hash": content_hash,
        "last_checked": now,
        "last_changed": now if entry.get("hash") != content_hash else entry.get("last_changed", now),
        "extraction_method": extraction_method,
        "content": content,
        "check_count": entry.get("check_count", 0) + 1,
    })

    checkpoint["sources"][url] = entry


def get_previous_content(checkpoint: dict[str, Any], url: str) -> str | None:
    """Retrieve the previously stored content for a source URL."""
    sources = checkpoint.get("sources", {})
    entry = sources.get(url)
    if entry:
        return entry.get("content")
    return None


def record_scrape_failure(
    checkpoint: dict[str, Any],
    url: str,
) -> int:
    """Record a scrape failure for a source. Returns consecutive failure count."""
    if "sources" not in checkpoint:
        checkpoint["sources"] = {}

    entry = checkpoint["sources"].get(url, {})
    consecutive_failures = entry.get("consecutive_failures", 0) + 1

    entry["consecutive_failures"] = consecutive_failures
    entry["last_failure"] = datetime.now(timezone.utc).isoformat()
    entry["last_checked"] = datetime.now(timezone.utc).isoformat()
    entry["check_count"] = entry.get("check_count", 0) + 1

    checkpoint["sources"][url] = entry
    return consecutive_failures


def clear_failure_count(checkpoint: dict[str, Any], url: str) -> None:
    """Clear consecutive failure count on successful scrape."""
    sources = checkpoint.get("sources", {})
    entry = sources.get(url)
    if entry:
        entry["consecutive_failures"] = 0
