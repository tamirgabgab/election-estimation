# Saving usage: tips and recommendations

Practical guidance built on the rules in [limits-plans.md](limits-plans.md) (subscription
and Claude Code) and [limits-api.md](limits-api.md) (API). Ordered by impact. "Official"
marks tips stated by Anthropic; the rest are conclusions from the rules and from this
project's history.

## 1. Context is the main cost

Every request re-sends the whole conversation, so its length multiplies everything else.

- Start a new conversation (`/clear`) for unrelated work. Official: one of the two
  highest-impact habits. Use `/rename` first if you may come back (`/resume`).
- `/compact` with a focus at natural breakpoints (end of a feature, before a new phase):
  `/compact keep the build procedure and open questions`. Do it while the cache is warm,
  not after a long break.
- Keep `CLAUDE.md` short (official: under 200 lines); move procedures into skills that load
  only when needed.
- Read only what you need: `head`, `grep`, `sed -n`, line ranges. Never dump a large CSV,
  a minified HTML report or a JSONL transcript into the conversation.
- Keep command output short: `| tail -3`, `grep -c`, `--stat`, `-q`. A test or build that
  prints 500 lines costs those tokens on every later request.
- Images are expensive: crop screenshots to the area you need, one per check, and do not
  re-read the same image.
- Do not re-read a file after editing it.

## 2. Model and effort

- Match the model to the job (official): Sonnet handles most coding, Haiku is enough for
  search, extraction and simple subagents, Opus/Fable for hard reasoning and design.
- Lower effort for simple tasks (official); keep `high`/`max` for real reasoning.
- Pick model and effort at the start of a conversation. Switching models mid-session
  re-reads the whole history uncached; switching effort also does on older models.
- Fast mode on a subscription is billed only from usage credits; turn it on at the start
  of a session, never in the middle (separate cache).

## 3. Subagents, workflows and parallel work

- Each subagent is a separate conversation with its own context and its own requests, all
  counted against the same limits. Use one only when it saves context or time: a broad
  search, a long research task, independent work in parallel.
- Give subagents a cheap model when the task allows (`model: haiku` / `sonnet`). The
  built-in Explore agent runs on Opus on subscriptions.
- Brief them precisely and ask for a short report: the report enters the main context.
- Do not duplicate a delegated task, and do not poll background work; wait for the
  notification.
- Workflows and agent teams multiply usage (teams about 7x). One heavy fan-out can use up
  the weekly limit before the session window resets. Estimate first; keep to the size
  guideline.

## 4. The cache works for you

- Cached input costs 0.1x or less of normal input and does not count toward API input
  rate limits.
- In Claude Code on a subscription the main conversation keeps a 1-hour cache: continuing
  within the hour is cheap; resuming a large conversation after hours costs a full re-read.
  Finish or `/compact` a large conversation before a long break.
- Things that break the cache: model switch, fast-mode toggle, tool or MCP changes, and in
  the API also thinking or effort changes and images added to the messages.
- API: put static content first, the breakpoint on the last unchanging block, and check
  hit rates (`/usage` "Prompt cache" line in Claude Code; the usage page in the Console).

## 5. Plan the work

- Write one specific prompt with all the context instead of several vague ones (official).
- Use plan mode for large changes, and stop early (Esc, `/rewind`) when the direction is
  wrong. A wrong long run is the most expensive mistake.
- Batch related questions into one message; batch similar requests (official).
- Prefer CLI tools (`gh`, `git`) over MCP servers with large tool lists; disable unused
  MCP servers (official). Check with `/context` and `/mcp`.
- Turn off prompt suggestions if you do not use them (they are background requests).

## 6. Watch and react

- `/usage` shows the plan bars, the reset times and what used the most (skills, subagents,
  MCP); `f` applies its suggestions. `/context` shows what fills the window.
- Near a limit: finish the current step, commit, and leave a short handoff note so the next
  session can start small. Switching model family helps only for an Opus or Sonnet limit,
  not for the session or weekly limit.
- Auto-continue resumes after a 5-hour reset (not a weekly one). Usage credits continue
  at API prices: set a monthly spend limit first.

## 7. API

- Use the Batch API (50% off) for anything that can wait up to 24 hours; combine with
  caching (1-hour TTL for batches sharing a prefix).
- Count tokens with the free token counting endpoint for the target model (Claude 4.7+
  produces about 30% more tokens for the same text).
- Set `max_tokens`, request short answers, use `low`/`medium` effort where quality holds.
- Handle 429 by honoring `retry-after`; ramp traffic up gradually; set a monthly spend limit.

## 8. In this project

- `python scripts/build_data.py` takes over two minutes and rewrites all workbooks: run it
  once at the end of a change, in the background, and read only its summary lines. For
  report-only changes run `python scripts/build_reports.py`.
- `reports/index.html` is about 1.3 MB and `data/processed/ballots_long.csv.gz` about 56 MB:
  never read them whole.
- `scripts/check_excel.py` is slow: check only the workbooks that changed.
- `scripts/check_reports.js` prints 24 lines; filter with `grep -c ": ok"` and `grep FAIL`.
- Read `HANDOFF.md` by section (`grep -n "^#"`, then `sed -n`), not whole.
- Web research (party names, leaders, sources): one well-briefed background agent per
  topic, writing results to a file in the scratchpad, instead of many searches in the
  main conversation.
