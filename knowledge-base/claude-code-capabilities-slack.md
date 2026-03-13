<\!-- Source: https://code.claude.com/docs/en/slack | Scraped: 2026-03-13 -->

# Claude Code in Slack

Claude Code in Slack brings Claude Code directly into Slack workspaces. When you mention `@Claude` with a coding task, Claude detects the intent and creates a Claude Code session on the web (claude.ai/code), allowing you to delegate development work without leaving team conversations.

Built on the existing Claude for Slack app with intelligent routing to Claude Code on the web for coding requests.

## Use Cases

- Bug investigation and fixes from Slack reports
- Quick code reviews and modifications from team feedback
- Collaborative debugging using thread context
- Parallel task execution -- kick off tasks while you continue other work

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Claude Plan | Pro, Max, Teams, or Enterprise with Claude Code access (premium seats) |
| Claude Code on the web | Must be enabled |
| GitHub Account | Connected to Claude Code on the web with at least one repo |
| Slack Authentication | Slack account linked to Claude account |

## Setup

1. Workspace admin installs Claude app from Slack App Marketplace
2. Authenticate individual Claude account via App Home -> Connect
3. Configure Claude Code on the web at claude.ai/code (connect GitHub, authenticate repos)
4. Choose routing mode:
   - **Code only**: All @mentions -> Claude Code sessions
   - **Code + Chat**: Intelligent routing between Code and Chat (with retry buttons)
5. Add Claude to channels: `/invite @Claude`

## How It Works

1. @mention Claude with coding request
2. Claude detects coding intent
3. New Claude Code session created on claude.ai/code
4. Progress updates posted to Slack thread
5. Completion: @mentions you with summary + action buttons
6. Review: "View Session" for transcript, "Create PR" for pull request

### Context Gathering
- **Threads**: gathers context from all thread messages
- **Channels**: looks at recent channel messages

### UI Elements
- **View Session**: full transcript on web
- **Create PR**: create pull request from changes
- **Retry as Code**: re-route chat response to Code session
- **Change Repo**: select different repository

## Access and Permissions

- Each user runs sessions under their own Claude account
- Usage counts against individual user's plan limits
- Users can only access repos they have personally connected
- Sessions appear in Claude Code history on claude.ai/code

### Channel-Based Access Control
- Claude only responds in channels where invited
- Admins control access by managing which channels have Claude
- Works in public and private channels (NOT DMs)

## Limitations

- GitHub only (no GitLab)
- One PR per session
- Rate limits apply per user plan
- Requires Claude Code on the web access
- Only works in channels, not DMs
