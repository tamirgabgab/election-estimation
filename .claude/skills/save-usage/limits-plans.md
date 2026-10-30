# Claude plans and Claude Code: usage limit rules

Collected from Anthropic's official pages on 2026-10-30. Pages show only relative dates
("updated this week"). The Pro and Max usage help articles could not be fetched (404 at
the known IDs), so their content is covered only through the pages below. Message counts
seen on third-party sites (e.g. "45 messages per 5 hours", peak-hour multipliers, 2026
limit boosts) are NOT confirmed and are left out. Check the live numbers in Claude Code
with `/usage` or on https://claude.ai/settings/usage.

## Plans

Source: https://claude.com/pricing

| Plan | Price | Usage |
|---|---|---|
| Free | $0 | No Opus |
| Pro | $20/mo monthly, $17/mo annual | "at least 5x more usage per 5-hour session than Free"; Fable via usage credits |
| Max 5x / 20x | from $100/mo | "5x or 20x the usage of Pro per 5-hour session"; Fable up to "50% of weekly limits" |
| Team | standard $25/seat monthly ($20 annual); premium $125 ($100 annual) | premium seats get "5x more usage than standard seats" |
| Enterprise | $20/seat/mo annual, 20 seats minimum, plus usage at API rates | |

No page publishes exact message or token counts; allowances are multipliers.

## Windows

- Session limit: "reset[s] on a rolling five-hour window, and paid plans add weekly
  limits on top" (pricing FAQ). Pro article: "reset every five hours".
- Weekly limit across all models on Pro and Max; it resets "at a fixed time each week
  that is assigned to your account" (shown in Settings > Usage).
  https://support.claude.com/en/articles/8325606-what-is-the-claude-pro-plan
- Max also has a separate weekly limit for Fable models.
  https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans
- "Usage counts against the session and weekly allowances at the same time. A single
  burst of heavy activity, such as a large workflow fanout, can exhaust the weekly
  allowance before the session window resets." https://code.claude.com/docs/en/errors.md
- Team and Enterprise: per-seat allowance on a rolling 5-hour and a weekly window,
  shared with Claude chat and Cowork. https://code.claude.com/docs/en/costs.md
- Anthropic "may limit your usage in other ways, such as weekly and monthly caps or model
  and feature usage, at our discretion" (Pro article).

## Model-specific limits

Source: https://code.claude.com/docs/en/errors.md

- Messages: "You've hit your session limit", "weekly limit", "Opus limit", "Sonnet
  limit", each with a reset time. Opus and Sonnet limits apply only to that model family,
  so `/model` to another family keeps you working. Session and weekly limits are shared
  by all models, so switching does not help there.
- Which plans carry Opus / Sonnet limits is not published; no Haiku limit is documented.

## What counts

- Message length, attached files, conversation length, model or feature (Pro article);
  tool use such as Research and web search, effort level, artifacts, multi-step tasks
  like running code or browsing (best-practices article, paraphrased).
  https://support.claude.com/en/articles/9797557-usage-limit-best-practices
- One shared pool: "These limits are shared across Claude and Claude Code" - claude.ai,
  desktop, mobile, CLI, IDE extensions and cloud sessions.
  https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- Subagents send their own requests, which "count toward the same usage limits as your
  main conversation". https://code.claude.com/docs/en/sub-agents.md
- Prompt suggestions count toward usage. https://code.claude.com/docs/en/interactive-mode.md
- Cloud sessions count toward plan usage; no separate VM charge.
  https://code.claude.com/docs/en/claude-code-on-the-web.md
- Scheduled tasks draw subscription usage like interactive sessions, plus run caps (100
  scheduled runs per hour per account; 30 "Run now" / API fires per hour per task).
  https://code.claude.com/docs/en/routines.md
- Workflows: "Runs count toward your plan's usage and rate limits"; up to 16 concurrent
  agents, 1,000 per run; a "Large workflow" warning above 25 agents or a projected 1.5M
  tokens; default size guideline `medium` (`small` on Pro). Ultracode makes a session
  reach its limits sooner. https://code.claude.com/docs/en/workflows.md
- Agent teams use "approximately 7x more tokens than standard sessions when teammates run
  in plan mode". https://code.claude.com/docs/en/costs.md
- Up to 20 concurrent subagents per session by default
  (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).

## At the limit

- Claude Code blocks requests until the reset time in the message.
- Wrap-up: a "small and capped" allowance to finish a response in progress ("Usage limit
  reached · wrapping up"); once per week on Pro, at each 5-hour limit on Max; counts
  toward the weekly limit.
- Auto-continue (CLI v2.1.234+, claude.ai sign-in): waits and resumes after the reset, at
  most twice in a row, not when the reset is more than 24 hours away. Setting
  `autoContinueAtUsageLimit`. Workflows pause and resume under the same conditions.
- Options: upgrade (Pro → Max 5x → Max 20x), usage credits, Console API credits, or wait.

## Extra usage (usage credits)

Source: https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans

- For Pro, Max 5x and Max 20x. With credits on, requests past the included limits
  "switch to pay-as-you-go pricing and continue", at standard API rates, until the
  monthly spend limit or the balance runs out. Enable in Settings > Usage (`/usage-credits`).
- Credits do not change when limits reset and generally do not expire.
- Max's monthly API credits (pricing page: $100-200) "can't be used in Claude Code or the
  Claude apps" per the help articles: the pages disagree.
- Fast mode on subscriptions runs only on usage credits, "even if you have remaining usage
  on your plan" (Opus 5.5: $8 / $40 per MTok). Its cache is separate, so switching it on
  mid-conversation re-reads the whole conversation uncached.
  https://code.claude.com/docs/en/fast-mode.md
- Ultrareview: 3 free runs on Pro and Max, then about $5-25 in credits per review.

## Models, context and cache in Claude Code

Sources: https://code.claude.com/docs/en/model-config.md,
https://code.claude.com/docs/en/prompt-caching.md, https://code.claude.com/docs/en/context-window.md

- Default model on Pro, Max, Team, Enterprise and API: Opus 5.5. Aliases `opus`, `sonnet`,
  `haiku`, `opusplan` (Opus to plan, Sonnet to execute). No automatic Opus → Sonnet switch
  at a usage threshold is documented; fallbacks happen only on overload or errors, for
  one turn.
- Default effort: `medium` on Opus 5.5, Sonnet 5.5 and Haiku 5.5; `high` elsewhere.
- Subagents inherit the main model by default; the built-in Explore subagent runs on Opus
  on subscriptions. Override with `model:` in the subagent definition or
  `CLAUDE_CODE_SUBAGENT_MODEL`.
- 1M context window by default on current models; auto-compaction at about 967K tokens
  (settable 100K-1M with `/autocompact`). Compaction re-injects CLAUDE.md, memory, up to
  five recent files and invoked skills (5,000 tokens per skill, 25,000 total).
- Cache: on a subscription within included usage the main conversation uses the 1-hour
  TTL; on usage credits, API key or cloud providers, 5 minutes. Subagents use 5 minutes.
- "Each model has its own cache": `/model` mid-session re-reads the whole history
  uncached. On Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.1, changing effort keeps the
  cache; on most other models it invalidates it.
- `/compact` while the cache is warm is cheap; after a break longer than the cache
  lifetime it costs the most.

## Commands

- `/usage` (aliases `/cost`, `/stats`): session cost, plan limits, a breakdown by skills,
  subagents, plugins and MCP servers, prompt-cache hit share, `d`/`w` for 24 hours or
  7 days, `f` to apply fixes.
- `/context`: context window by category. `/status`: version, model, account.
- `/compact [focus]`, `/clear`, `/model`, `/effort`, `/autocompact`, `/fast`.
