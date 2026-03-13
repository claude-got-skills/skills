<\!-- Source: https://code.claude.com/docs/en/remote-control | Scraped: 2026-03-13 -->

# Remote Control

**Status:** Available on all plans (Pro, Max, Team, Enterprise). Team/Enterprise admins must enable Claude Code in admin settings first. API keys not supported.

Remote Control connects claude.ai/code or the Claude mobile app (iOS/Android) to a Claude Code session running on your machine. Start a task at your desk, then pick it up from your phone or another browser.

Key difference from Claude Code on the web: Remote Control executes on YOUR machine (local filesystem, MCP servers, tools, project config stay available). Claude Code on the web executes in Anthropic-managed cloud infrastructure.

## Capabilities

- **Full local environment remotely**: filesystem, MCP servers, tools, project config all stay available
- **Work from both surfaces at once**: conversation stays in sync across all connected devices
- **Survive interruptions**: auto-reconnects when machine comes back online after sleep/network drop

## Requirements

- Subscription: Pro, Max, Team, or Enterprise
- Authentication: run `claude` and use `/login` to sign in
- Workspace trust: run `claude` in project directory at least once

## Start a Session

### New session
```bash
claude remote-control
# Flags:
#   --name "My Project"  -- custom session title
#   --verbose            -- detailed connection logs
#   --sandbox / --no-sandbox -- enable/disable sandboxing (off by default)
```

Press spacebar to show QR code for phone access.

### From existing session
```
/remote-control
# or /rc
# Optional: /remote-control My Project
```

## Connect from Another Device

- Open the session URL displayed in terminal
- Scan the QR code with Claude mobile app
- Open claude.ai/code and find session by name (shows computer icon with green dot when online)
- Use `/mobile` command for download QR code for iOS/Android app

## Enable for All Sessions

Run `/config` -> set "Enable Remote Control for all sessions" to true.

Each Claude Code instance supports one remote session at a time.

## Connection and Security

- Outbound HTTPS only -- never opens inbound ports
- Registers with Anthropic API and polls for work
- All traffic over TLS through Anthropic API
- Multiple short-lived credentials, each scoped to single purpose

## Remote Control vs Claude Code on the Web

| Aspect | Remote Control | Claude Code on the Web |
|--------|---------------|----------------------|
| Execution | Your machine | Anthropic cloud |
| Local env | Full access | No (cloud clone) |
| Use when | Middle of local work, want to continue from another device | No local setup needed, parallel tasks, remote repos |

## Limitations

- One remote session per Claude Code instance
- Terminal must stay open (process exits = session ends)
- Extended network outage (~10 min) causes timeout
