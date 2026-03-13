# Distill Web Monitor — Anthropic Capability Tracking

Configuration guide for monitoring Anthropic web pages for product-relevant changes using the [Distill.io](https://distill.io) browser extension.

---

## Quick Setup Checklist

1. Install [Distill Web Monitor](https://chrome.google.com/webstore/detail/distill-web-monitor/inlikjemeeknofcgfcdgalmequhdnaio) Chrome extension
2. Create 8 monitors using the configurations below
3. Set email notifications (default channel)
4. Bookmark this guide for the new-page workflow (Section 4)

---

## 1. Monitor Configurations

Each entry below gives you the exact settings to enter in Distill's "Add Monitor" flow. When adding a monitor, choose **"Monitor parts of page"** and enter the CSS selector listed.

### 1.1 API Overview

| Field | Value |
|---|---|
| **URL** | `https://platform.claude.com/docs/en/build-with-claude/overview` |
| **Name** | `Anthropic — API Overview` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `main` |
| **Check interval** | Every 24 hours |
| **Conditions** | Text was added OR text was removed |

**What to watch for:** New feature additions, capability changes, deprecation notices.
**Noise filter:** Ignore minor wording tweaks — look for new sections or removed capabilities.

---

### 1.2 API Release Notes ⭐ HIGH PRIORITY

| Field | Value |
|---|---|
| **URL** | `https://platform.claude.com/docs/en/release-notes/overview` |
| **Name** | `Anthropic — API Release Notes ⭐` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `main` |
| **Check interval** | Every 6 hours |
| **Conditions** | Text was added |

**Why high priority:** New API releases appear here first. This is the highest-signal page.
**What to watch for:** Any new release notes entry (typically appears at the top of the page).

---

### 1.3 Features & Capabilities Collection 🔍 NEW PAGE DETECTION

| Field | Value |
|---|---|
| **URL** | `https://support.claude.com/en/collections/18031719-features-and-capabilities` |
| **Name** | `Anthropic — Features & Capabilities (collection)` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `section[data-testid="main-content"]` |
| **Check interval** | Every 12 hours |
| **Conditions** | Text was added |

**Critical role:** This is the **new-page detection** monitor. When Anthropic adds a new feature (e.g., "fast mode" on 7 Feb 2026), it gets its own page that appears as a new link in this collection. When you get a notification from this monitor, follow the **New Page Workflow** in Section 4.

**Fallback selector** (if `data-testid` changes): `a[data-testid="article-link"]`

---

### 1.4 Claude.ai Release Notes

| Field | Value |
|---|---|
| **URL** | `https://support.claude.com/en/articles/12138966-release-notes` |
| **Name** | `Anthropic — Claude.ai Release Notes` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `article[class*="intercom-force-break"]` |
| **Check interval** | Every 12 hours |
| **Conditions** | Text was added |

**What to watch for:** New entries at the top of the page. Release notes are organized under `<h2>` date headings.
**Fallback selector:** `section[data-testid="main-content"]`

---

### 1.5 Claude in Excel

| Field | Value |
|---|---|
| **URL** | `https://support.claude.com/en/articles/12650343-using-claude-in-excel` |
| **Name** | `Anthropic — Claude in Excel` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `article[class*="intercom-force-break"]` |
| **Check interval** | Every 24 hours |
| **Conditions** | Text was added OR text was removed |

**What to watch for:** Capability changes, new features, updated instructions.

---

### 1.6 Claude in PowerPoint

| Field | Value |
|---|---|
| **URL** | `https://support.claude.com/en/articles/13521390-using-claude-in-powerpoint` |
| **Name** | `Anthropic — Claude in PowerPoint` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `article[class*="intercom-force-break"]` |
| **Check interval** | Every 24 hours |
| **Conditions** | Text was added OR text was removed |

**What to watch for:** Capability changes, new features, updated instructions.

---

### 1.7 Getting Started with Cowork

| Field | Value |
|---|---|
| **URL** | `https://support.claude.com/en/articles/13345190-getting-started-with-cowork` |
| **Name** | `Anthropic — Getting Started with Cowork` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `article[class*="intercom-force-break"]` |
| **Check interval** | Every 24 hours |
| **Conditions** | Text was added OR text was removed |

**What to watch for:** Capability changes, workflow updates, new features.

---

### 1.8 Claude Code CHANGELOG

| Field | Value |
|---|---|
| **URL** | `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md` |
| **Name** | `Anthropic — Claude Code CHANGELOG` |
| **Mode** | Monitor parts of page |
| **CSS Selector** | `article.markdown-body` |
| **Check interval** | Every 12 hours |
| **Conditions** | Text was added |

**What to watch for:** New version entries (appear at the top of the changelog).
**Note:** GitHub occasionally changes its DOM. If this selector stops working, try `div[data-target="readme-toc.content"]` or fall back to monitoring the entire page.

---

## 2. Notification Settings

In Distill extension → Settings → Notifications:

| Setting | Value |
|---|---|
| **Channel** | Email (default) |
| **Digest mode** | Off (get individual alerts) |
| **Include diff** | Yes — shows exactly what changed |

For the two ⭐ high-priority monitors (API Release Notes + Features Collection), consider also enabling **browser push notifications** for faster awareness.

---

## 3. Selector Troubleshooting

Anthropic's support pages use Intercom (React/Next.js with Tailwind). The docs platform is custom-built. Both can change their DOM structure during redesigns.

**If a selector stops working:**

| Page type | Try these selectors in order |
|---|---|
| **support.claude.com articles** | 1. `article[class*="intercom-force-break"]` → 2. `section[data-testid="main-content"]` → 3. `#main-content` → 4. Full page |
| **support.claude.com collection** | 1. `section[data-testid="main-content"]` → 2. `a[data-testid="article-link"]` → 3. Full page |
| **platform.claude.com docs** | 1. `main` → 2. `article` → 3. `div[role="main"]` → 4. Full page |
| **GitHub** | 1. `article.markdown-body` → 2. `div[data-target="readme-toc.content"]` → 3. Full page |

**Testing a selector:** In Distill's visual selector tool, after choosing "Monitor parts of page," click the element you want and verify the highlighted area covers only the content — not the navigation, sidebar, or footer.

---

## 4. New Page Detection Workflow

When you receive a change notification from **Monitor 1.3 (Features & Capabilities collection):**

### Step 1 — Identify what changed
Open the Distill diff. Look for **new article links** that weren't there before (new `<a>` elements with article titles).

### Step 2 — Visit the new page
Click the new link to see the full feature page (e.g., `https://support.claude.com/en/articles/XXXXXXX-new-feature-name`).

### Step 3 — Decide whether to monitor
If the new page describes a capability relevant to our product development:

- **Add a new Distill monitor** using the same pattern as monitors 1.5–1.7:
  - Mode: Monitor parts of page
  - Selector: `article[class*="intercom-force-break"]`
  - Interval: 24 hours
  - Conditions: Text was added OR text was removed

### Step 4 — Update our tracking files
1. Add the new URL to `claude-urls-to-monitor.md` in the workspace
2. Fetch the page content for the local knowledge base
3. Note the date the feature was first detected

### Future automation
This workflow is currently manual. A potential automation path: a script that periodically diffs the collection page's link list and auto-creates monitors via Distill's API (requires Distill Pro).

---

## 5. Summary Table

| # | Monitor | Selector | Interval | Priority |
|---|---|---|---|---|
| 1.1 | API Overview | `main` | 24h | Normal |
| 1.2 | API Release Notes | `main` | 6h | ⭐ High |
| 1.3 | Features & Capabilities | `section[data-testid="main-content"]` | 12h | 🔍 Detection |
| 1.4 | Claude.ai Release Notes | `article[class*="intercom-force-break"]` | 12h | High |
| 1.5 | Claude in Excel | `article[class*="intercom-force-break"]` | 24h | Normal |
| 1.6 | Claude in PowerPoint | `article[class*="intercom-force-break"]` | 24h | Normal |
| 1.7 | Cowork Getting Started | `article[class*="intercom-force-break"]` | 24h | Normal |
| 1.8 | Claude Code CHANGELOG | `article.markdown-body` | 12h | High |

---

*Last updated: 10 February 2026*
