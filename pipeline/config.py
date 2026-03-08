"""Source URL registry, path constants, and environment loading."""

import os
from dataclasses import dataclass
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).parent
PROJECT_DIR = PIPELINE_DIR.parent
REPORTS_DIR = PIPELINE_DIR / "reports"
CHECKPOINT_FILE = PIPELINE_DIR / "checkpoint.json"
RUN_HISTORY_FILE = PIPELINE_DIR / "run-history.json"
LOG_DIR = PROJECT_DIR / "logs"

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


# ── Environment ──────────────────────────────────────────────────────────────

def load_env() -> dict[str, str]:
    """Load .env file from project root if it exists."""
    env_file = PROJECT_DIR / ".env"
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    value = value.strip().strip("'\"")
                    env_vars[key.strip()] = value
                    os.environ.setdefault(key.strip(), value)
    return env_vars


def get_jina_headers() -> dict[str, str]:
    """Return headers for Jina Reader requests, with optional API key."""
    headers = {"Accept": "text/plain"}
    jina_key = os.environ.get("JINA_API_KEY")
    if jina_key:
        headers["Authorization"] = f"Bearer {jina_key}"
    return headers


# ── Source Registry ──────────────────────────────────────────────────────────

@dataclass
class Source:
    """A monitored documentation source."""
    url: str
    name: str
    page_type: str      # api-docs, support, github, claude-code
    priority: str       # HIGH or normal
    kb_files: list[str] # knowledge-base files this source maps to

    @property
    def is_high_priority(self) -> bool:
        return self.priority == "HIGH"


SOURCES: list[Source] = [
    Source(
        url="https://platform.claude.com/docs/en/release-notes/overview",
        name="API Release Notes",
        page_type="api-docs",
        priority="HIGH",
        kb_files=["api-release-notes.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/overview",
        name="API Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["api-overview.md"],
    ),
    Source(
        url="https://support.claude.com/en/articles/claude-ai-release-notes",
        name="Claude AI Release Notes",
        page_type="support",
        priority="HIGH",
        kb_files=["claude-ai-release-notes.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/build-with-claude/overview",
        name="Build with Claude Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["build-with-claude.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/about-claude/models/overview",
        name="Models Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["models-overview.md"],
    ),
    Source(
        url="https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md",
        name="Claude Code CHANGELOG",
        page_type="github",
        priority="HIGH",
        kb_files=["claude-code-changelog.md"],
    ),
    Source(
        url="https://code.claude.com/docs/agent-teams",
        name="Claude Code Agent Teams",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-agent-teams.md"],
    ),
    Source(
        url="https://code.claude.com/docs/hooks",
        name="Claude Code Hooks",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-hooks.md"],
    ),
    Source(
        url="https://code.claude.com/docs/skills",
        name="Claude Code Skills",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-skills.md"],
    ),
    Source(
        url="https://code.claude.com/docs/plugins",
        name="Claude Code Plugins",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-plugins.md"],
    ),
    Source(
        url="https://code.claude.com/docs/cli-reference",
        name="Claude Code CLI Reference",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-cli-reference.md"],
    ),
    Source(
        url="https://code.claude.com/docs/extensions",
        name="Claude Code Extensions",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-extensions.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/build-with-claude/context-windows",
        name="Context Windows",
        page_type="api-docs",
        priority="normal",
        kb_files=["context-windows.md"],
    ),
]


def get_source_by_url(url: str) -> Source | None:
    """Look up a source by its URL."""
    for source in SOURCES:
        if source.url == url:
            return source
    return None


def get_sources_by_priority(priority: str) -> list[Source]:
    """Filter sources by priority level."""
    return [s for s in SOURCES if s.priority == priority]
