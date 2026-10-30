---
name: save-usage
description: Work in a way that saves Claude usage limits and tokens. Use at the start of a long or heavy task (rebuilds, multi-file changes, web research, subagents or workflows), when the user mentions usage, limits, quota, tokens, cost or saving (מכסה, מכסות, חיסכון, טוקנים), when /usage or a limit warning shows the session or weekly limit is getting close, or before deciding whether to spawn agents. Holds a checklist plus the official limit rules (plans, Claude Code, API) and tips.
---

# Save usage

Usage limits are shared by claude.ai, the apps and every Claude Code surface, and count
the session (rolling 5 hours) and the weekly window at the same time. Every request
re-sends the whole conversation, so context size multiplies every other cost. Rules and
sources: [limits-plans.md](limits-plans.md), [limits-api.md](limits-api.md); reasoning
and detail: [tips.md](tips.md).

## Before a task

1. **Scope** - is this one task or several? Unrelated work belongs in a new conversation
   (suggest `/clear` or a new session to the user, with a short handoff note).
2. **Cost estimate** - if the plan needs a full rebuild, many screenshots, web research or
   more than one subagent, say so in one line and pick the cheapest route that still
   gives a correct result.
3. **Model and effort** - do not suggest switching models mid-conversation (it re-reads the
   history uncached). For a light task in a new session, suggest Sonnet or a lower effort.

## While working

- Read narrowly: `grep -n`, `head`, `sed -n 'a,bp'`, `--stat`; never whole large files
  (CSV, generated HTML, transcripts, logs).
- Keep output short: pipe to `tail`, `grep -c`, `-q`; print only the lines you act on.
- Edit in place; do not re-read a file after an edit or a write.
- Screenshots: one per check, cropped to the region that matters.
- Long commands (builds, checks): run in the background and wait for the notification;
  never poll with repeated status reads.
- Independent tool calls go in one message.

## Subagents and workflows

- Spawn only for real parallel work, broad searches or long research whose raw output
  should stay out of the main context. Otherwise do it inline.
- Brief completely (goal, files, what is ruled out, output file and format) and ask for a
  short report; set a cheaper `model` when the task is simple (search, extraction).
- One agent per independent topic; never duplicate its work while it runs.
- Workflows and agent teams only when the user asked for them; state the expected size.

## Near a limit

- Check with `/usage` (suggest it to the user; the CLI shows reset times and the biggest
  consumers).
- Finish the current step, commit and push (if the project uses git), update the
  project's status or handoff notes if it keeps them, then tell the user what is left.
  A weekly limit is not helped by switching models; an Opus or Sonnet limit is.
- Do not start a large fan-out or a full rebuild late in a window.

## Project-specific rules

- Look for a "Usage limits" section in the project's `CLAUDE.md` (slow commands, files too
  large to open, noisy checks) and follow it together with this skill.
- When you notice such a cost in a project (a build that takes minutes, a generated file of
  megabytes, a test run that prints hundreds of lines), propose adding a line for it to
  that section.

## Keeping this skill current

The numbers in the reference files are as of 2026-10-30. When the user asks about limits,
re-check the official pages listed there (pricing, support articles, Claude Code costs
docs, API rate limits) before quoting a number, and update the files with the date.
