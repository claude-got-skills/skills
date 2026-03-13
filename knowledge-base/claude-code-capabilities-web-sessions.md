<\!-- Source: https://code.claude.com/docs/en/claude-code-on-the-web | Scraped: 2026-03-13 -->

# Claude Code on the Web

**Status:** Research preview
**Available to:** Pro, Max, Team, Enterprise (premium seats or Chat + Claude Code seats)
**URL:** claude.ai/code
**Also available on:** Claude iOS and Android apps

Claude Code on the web lets developers kick off Claude Code sessions from the browser or mobile app, running on Anthropic-managed cloud infrastructure.

## Best For

- Answering questions about code architecture
- Bug fixes and routine, well-defined tasks
- Parallel work (multiple bug fixes simultaneously)
- Repositories not cloned locally
- Backend changes where Claude can write tests then code

## Getting Started

1. Visit claude.ai/code
2. Connect GitHub account
3. Install Claude GitHub app in repositories
4. Select default environment
5. Submit coding task
6. Review changes in diff view, iterate, create PR

## How It Works

1. **Repository cloning**: Repo cloned to Anthropic-managed VM
2. **Environment setup**: Secure cloud environment prepared, setup script runs
3. **Network configuration**: Internet access configured per settings
4. **Task execution**: Claude analyzes, changes, tests, checks
5. **Completion**: Notification + PR creation
6. **Results**: Changes pushed to branch

## Diff View

See exactly what Claude changed before creating PR. Diff stats indicator shows lines added/removed. Can review file by file, comment on changes, iterate with Claude.

## Moving Tasks Between Web and Terminal

### Terminal to Web (--remote)
```bash
claude --remote "Fix the authentication bug in src/auth/login.ts"
```
Creates new web session. Task runs in cloud while you work locally. Monitor via `/tasks`, claude.ai, or mobile app.

**Parallel execution**: Each --remote creates independent session:
```bash
claude --remote "Fix flaky test"
claude --remote "Update API docs"
claude --remote "Refactor logger"
```

### Web to Terminal (/teleport or --teleport)
- `/teleport` (or `/tp`): interactive picker of web sessions
- `claude --teleport`: interactive picker from command line
- `claude --teleport <session-id>`: resume specific session
- `/tasks` then press `t`: teleport into background session
- "Open in CLI" button on web

Requirements: clean git state, correct repository, branch pushed to remote, same account.

Session handoff is one-way: can pull web to terminal but not push terminal to web.

## Sharing Sessions

### Enterprise/Teams
- Private or Team visibility
- Team = visible to org members
- Repository access verification enabled by default
- Slack sessions auto-shared with Team visibility

### Max/Pro
- Private or Public visibility
- Public = visible to any logged-in claude.ai user
- Check for sensitive content before sharing
- Repository access verification available in Settings

## Cloud Environment

### Default Image (Ubuntu 24.04)
- Python 3.x with pip, poetry
- Node.js LTS with npm, yarn, pnpm, bun
- Ruby 3.1.6, 3.2.6, 3.3.6 (default 3.3.6) with rbenv
- PHP 8.4.14
- Java OpenJDK with Maven, Gradle
- Go latest stable
- Rust toolchain with cargo
- C++ with GCC and Clang
- PostgreSQL 16, Redis 7.0

### Setup Scripts
Bash scripts that run before Claude Code launches on new sessions.
- Run as root on Ubuntu 24.04
- Configure in environment settings UI
- Non-zero exit = session fails (use `|| true` for non-critical)
- Only on new sessions (skipped on resume)

### Setup Scripts vs SessionStart Hooks

| Aspect | Setup scripts | SessionStart hooks |
|--------|--------------|-------------------|
| Attached to | Cloud environment | Repository |
| Configured in | Cloud environment UI | .claude/settings.json |
| Runs | Before Claude Code, new sessions only | After Claude Code, every session |
| Scope | Cloud only | Both local and cloud |

### Environment Configuration
- `/remote-env`: choose default environment for --remote sessions
- Environment variables in .env format
- Network: Limited (default), No internet, or Full access

## Network Access

Default "Limited" mode allows common domains (package registries, GitHub, cloud platforms, etc.). Security proxy handles all outbound HTTPS traffic.

## Pricing and Rate Limits

Shares rate limits with all Claude and Claude Code usage. Multiple parallel tasks consume more proportionally.

## Limitations

- GitHub only (no GitLab for cloud sessions)
- Same-account requirement for session transfer
