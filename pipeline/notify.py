"""macOS notifications via osascript."""

import logging
import subprocess

logger = logging.getLogger(__name__)


def send_notification(
    title: str,
    message: str,
    subtitle: str = "",
    sound: str = "default",
) -> bool:
    """Send a macOS notification using osascript.

    Returns True if the notification was sent successfully, False otherwise.
    """
    # Escape double quotes for AppleScript
    title = title.replace('"', '\\"')
    message = message.replace('"', '\\"')
    subtitle = subtitle.replace('"', '\\"')

    script_parts = [f'display notification "{message}"']
    script_parts.append(f'with title "{title}"')
    if subtitle:
        script_parts.append(f'subtitle "{subtitle}"')
    if sound:
        script_parts.append(f'sound name "{sound}"')

    applescript = " ".join(script_parts)

    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            timeout=10,
        )
        logger.info("Notification sent: %s", title)
        return True
    except (subprocess.SubprocessError, OSError) as e:
        logger.warning("Failed to send notification: %s", e)
        return False


def notify_changes(changed_count: int, high_priority_count: int) -> bool:
    """Send a notification about detected changes."""
    if high_priority_count > 0:
        subtitle = f"{high_priority_count} high-priority"
    else:
        subtitle = ""

    return send_notification(
        title="Freshness Check: Changes Detected",
        message=f"{changed_count} source(s) have changed since last check.",
        subtitle=subtitle,
    )


def notify_errors(error_count: int, source_names: list[str]) -> bool:
    """Send a notification about scrape failures."""
    names = ", ".join(source_names[:3])
    if len(source_names) > 3:
        names += f" (+{len(source_names) - 3} more)"

    return send_notification(
        title="Freshness Check: Scrape Errors",
        message=f"{error_count} source(s) failed to scrape: {names}",
        sound="Basso",  # distinct error sound
    )


def notify_no_changes(source_count: int) -> bool:
    """Send a quiet notification that no changes were found."""
    return send_notification(
        title="Freshness Check: No Changes",
        message=f"All {source_count} sources unchanged.",
        sound="",  # silent
    )
