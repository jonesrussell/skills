---
name: archive-readiness
license: MIT
description: Check whether the current chat or task is safe to archive when the user says they want to wrap up, get ready to archive, confirm nothing is dangling, or move on. Report blockers and intentional residuals without creating an archive file.
---

# Archive Readiness

Treat "archive" as the user archiving the chat in the product UI unless they explicitly ask for an archive file or exported artifact.

## Closeout check

Inspect the current task using read-only checks appropriate to its scope. Do not manufacture work merely to make the checklist longer.

- Confirm the user's requested outcome was delivered, or identify what remains incomplete.
- Check for pending questions, approvals, tool calls, commands, active goals, agents, jobs, automations, or scheduled follow-ups created or managed in this task.
- For repository work, check the relevant working tree, unpublished commits, branch synchronization, and open pull requests when those facts determine whether work is dangling.
- For external mutations such as deployments, issue changes, purchases, or messages, distinguish verified completion from a claim that cannot currently be verified.
- Identify local-only artifacts, temporary worktrees, credentials, retained evidence, or future cleanup dates only when they were created or materially affected by this task.
- Separate real blockers from intentionally parked residual work. An open research issue, disabled future feature, retention deadline, or documented follow-up is not dangling when it has a clear owner and no action is currently authorized.

Do not turn closeout into another improvement cycle. Avoid new documentation, reviews, refactors, cleanup projects, or speculative safeguards unless they are necessary to resolve an actual archive blocker.

## Safety and scope

Archive readiness is read-only by default. Do not delete files, stop unrelated work, close issues, merge pull requests, deploy, send messages, or archive chats merely because the user asked for a readiness check. If cleanup is required, report the exact item and obtain any authorization normally required for that action.

Check only the current task and systems already in scope. Do not inventory every chat, repository, project, or automation on the account. If another assistant or external process is inaccessible, say that its state is unverified instead of claiming it is clean.

Do not create an archive summary file unless the user explicitly requests one.

## Report

Lead with one verdict:

- **Ready to archive** when no current-scope action, approval, unpublished work, or active process requires attention.
- **Not ready to archive** when something concrete is still running, unpublished, awaiting authorization, or required for the requested outcome.

Then give only the useful supporting facts:

- what was checked;
- any blocker and the smallest action needed;
- intentional residuals that remain tracked but require no action now;
- any boundary that could not be verified.

Keep the answer concise. If ready, explicitly tell the user they can archive the chat and move on.
