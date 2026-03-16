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
KB_DIR = PROJECT_DIR / "knowledge-base"
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
        kb_files=["claude-capabilities-features-overview.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/overview",
        name="API Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["claude-capabilities-features-overview.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/build-with-claude/overview",
        name="Build with Claude Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["claude-capabilities-features-overview.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/about-claude/models/overview",
        name="Models Overview",
        page_type="api-docs",
        priority="normal",
        kb_files=["claude-capabilities-new-in-opus-4-6.md"],
    ),
    Source(
        url="https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md",
        name="Claude Code CHANGELOG",
        page_type="github",
        priority="HIGH",
        kb_files=["claude-code-capabilities-use-cli.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/agent-teams",
        name="Claude Code Agent Teams",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-agent-teams.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/hooks",
        name="Claude Code Hooks",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-automate-with-hooks.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/skills",
        name="Claude Code Skills",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-skills.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/plugins",
        name="Claude Code Plugins",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-create-plugins.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/cli-reference",
        name="Claude Code CLI Reference",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-cli-reference.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/sub-agents",
        name="Claude Code Subagents",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-create-custom-subagents.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/interactive-mode",
        name="Interactive Mode",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-interactive-mode.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/commands",
        name="Built-in Commands",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-commands.md"],
    ),
    Source(
        url="https://platform.claude.com/docs/en/build-with-claude/context-windows",
        name="Context Windows",
        page_type="api-docs",
        priority="normal",
        kb_files=["claude-capabilities-context-windows.md"],
    ),
    # ── Claude Code features (code.claude.com) ────────────────────────────
    Source(
        url="https://code.claude.com/docs/en/code-review",
        name="Code Review",
        page_type="claude-code",
        priority="HIGH",
        kb_files=["claude-code-capabilities-code-review.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/remote-control",
        name="Remote Control",
        page_type="claude-code",
        priority="HIGH",
        kb_files=["claude-code-capabilities-remote-control.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/slack",
        name="Slack Integration",
        page_type="claude-code",
        priority="HIGH",
        kb_files=["claude-code-capabilities-slack.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/desktop",
        name="Desktop App",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-desktop.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/desktop-quickstart",
        name="Desktop Quickstart",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-desktop.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/claude-code-on-the-web",
        name="Claude Code on the Web",
        page_type="claude-code",
        priority="HIGH",
        kb_files=["claude-code-capabilities-web-sessions.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/jetbrains",
        name="JetBrains Plugin",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-jetbrains.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/vs-code",
        name="VS Code Extension",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-vscode.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/github-actions",
        name="GitHub Actions",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-ci-cd.md"],
    ),
    Source(
        url="https://code.claude.com/docs/en/gitlab-ci-cd",
        name="GitLab CI/CD",
        page_type="claude-code",
        priority="normal",
        kb_files=["claude-code-capabilities-ci-cd.md"],
    ),
    # ── API platform docs ─────────────────────────────────────────────────
    Source(
        url="https://platform.claude.com/docs/en/about-claude/pricing",
        name="Pricing Details",
        page_type="api-docs",
        priority="normal",
        kb_files=["claude-capabilities-new-in-opus-4-6.md"],
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


# ── KB-to-Target Mapping (Sprint 4) ─────────────────────────────────────────
#
# Maps each knowledge-base file to the user-facing files it can affect.
# The proposal engine uses this to determine which files to generate edit
# proposals for when a KB file is updated.
#
# Target file paths are relative to PROJECT_DIR.
# SKILL.md and quick-reference.md are only included for KB files that could
# affect load-bearing strings (model IDs, pricing, breaking changes).

SKILL_MD = "skills/assistant-capabilities/SKILL.md"
QUICK_REF = "data/quick-reference.md"
REF_API = "skills/assistant-capabilities/references/api-features.md"
REF_TOOLS = "skills/assistant-capabilities/references/tool-types.md"
REF_AGENT = "skills/assistant-capabilities/references/agent-capabilities.md"
REF_CODE = "skills/assistant-capabilities/references/claude-code-specifics.md"
REF_MODEL = "skills/assistant-capabilities/references/model-specifics.md"

PROPOSALS_DIR = PIPELINE_DIR / "proposals"
PROPOSALS_DIR.mkdir(exist_ok=True)

KB_TO_TARGETS: dict[str, list[str]] = {
    # ── API / platform capabilities ──────────────────────────────────────
    "claude-capabilities-new-in-opus-4-6.md": [
        SKILL_MD, QUICK_REF, REF_MODEL, REF_API,
    ],
    "claude-capabilities-pricing.md": [
        SKILL_MD, QUICK_REF, REF_MODEL,
    ],
    "claude-capabilities-features-overview.md": [
        SKILL_MD, QUICK_REF, REF_MODEL,
    ],
    "claude-capabilities-context-windows.md": [
        REF_API,
    ],
    "claude-capabilities-structured-outputs.md": [
        REF_API,
    ],
    "claude-capabilities-files-api.md": [
        REF_API,
    ],
    "claude-capabilities-memory-tool.md": [
        REF_API,
    ],
    "claude-capabilities-search-results-citations.md": [
        REF_API,
    ],
    "claude-capabilities-programmatic-tool-calling.md": [
        REF_API, REF_TOOLS,
    ],
    "claude-capabilities-pdf-support.md": [
        REF_API,
    ],
    "claude-capabilities-computer-use.md": [
        REF_TOOLS,
    ],
    "claude-capabilities-implement-tool-use.md": [
        REF_TOOLS,
    ],
    "claude-capabilities-mcp-via-api.md": [
        REF_TOOLS,
    ],
    # ── Agent / SDK capabilities ─────────────────────────────────────────
    "claude-capabilities-agent-sdk-overview.md": [
        REF_AGENT,
    ],
    "claude-capabilities-agent-sdk-python.md": [
        REF_AGENT,
    ],
    "claude-capabilities-agent-skills-via-api.md": [
        REF_AGENT, REF_API,
    ],
    "mcp-apps-overview.md": [
        REF_AGENT,
    ],
    # ── Claude Code capabilities ─────────────────────────────────────────
    "claude-code-capabilities-agent-teams.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-automate-with-hooks.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-ci-cd.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-cli-reference.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-interactive-mode.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-commands.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-code-review.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-create-custom-subagents.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-create-plugins.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-desktop.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-extension-options.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-jetbrains.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-mcp.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-plugin-reference.md": [
        REF_AGENT,
    ],
    "claude-code-capabilities-remote-control.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-sandboxing.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-skills.md": [
        REF_CODE, REF_AGENT,
    ],
    "claude-code-capabilities-slack.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-use-chrome-browser.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-use-cli.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-vscode.md": [
        REF_CODE,
    ],
    "claude-code-capabilities-web-sessions.md": [
        REF_CODE,
    ],
}


def get_targets_for_kb(kb_filename: str) -> list[str]:
    """Return target files affected by a KB file update.

    Falls back to an empty list for unmapped KB files.
    """
    return KB_TO_TARGETS.get(kb_filename, [])


def validate_kb_targets() -> list[str]:
    """Validate that all mapped target files exist on disk.

    Returns a list of error messages (empty if all valid).
    """
    errors = []
    for kb_file, targets in KB_TO_TARGETS.items():
        for target in targets:
            target_path = PROJECT_DIR / target
            if not target_path.exists():
                errors.append(f"Target '{target}' for KB '{kb_file}' not found")
    return errors
