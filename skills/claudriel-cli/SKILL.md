---
name: claudriel-cli
description: Use when the user wants to manage commitments, view their daily brief, or interact with Claudriel. Triggers include "add task", "what's on my plate", "mark done", "my commitments", "daily brief", "cl add", "cl list", "cl brief", "cl done".
---

# Claudriel CLI Integration

## Overview

Manage commitments and view the daily brief through the `cl` CLI, which authenticates against claudriel.ai via HMAC Bearer tokens.

## Commands

Run these via Bash tool:

| Command | Purpose |
|---------|---------|
| `cl brief` | Show daily brief (schedule, commitments, triage) |
| `cl add "title" --due YYYY-MM-DD --direction outbound` | Create a commitment (default: outbound, pending) |
| `cl list --status pending` | List commitments (filter: pending, active, completed, cancelled, overdue) |
| `cl done <uuid-prefix>` | Mark a commitment as completed (8-char prefix is enough) |

## Usage Patterns

**When the user mentions a task or commitment during conversation:**
- Offer to capture it: `cl add "the task title"`
- If they mention a deadline, add `--due YYYY-MM-DD`
- If someone owes them something, use `--direction inbound`

**When the user asks what's on their plate:**
- Run `cl brief` for the full picture
- Run `cl list --status pending` for just commitments

**When the user says they finished something:**
- Run `cl list` to find the matching commitment
- Run `cl done <uuid-prefix>` to mark it complete

## Notes

- Config lives at `~/.config/cl/config.toml`
- If auth fails, suggest `cl auth` to reconfigure
- The brief shows: schedule, pending commitments, waiting-on (inbound), triage, GitHub activity
- UUID prefixes: first 8 characters are usually unique enough
