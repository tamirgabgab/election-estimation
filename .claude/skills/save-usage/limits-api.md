# Claude API: limits and cost rules

Collected from Anthropic's official docs on 2026-10-30 (pages show no "last updated"
date; treat every number as "as shown on 2026-10-30"). Quotes come from page
extractions; spot-check the source before a billing decision.

## Rate limits and spend caps

Source: https://platform.claude.com/docs/en/api/rate-limits

- Limits are per organization. Tiers: Start, Build, Scale, Custom (contact sales).
  "Organizations are placed on a tier automatically based on usage history and account
  standing." New organizations may start in an Evaluation tier with lower, unpublished
  limits. Deposit requirements per tier are not published.
- Monthly spend caps: Start $500, Build $1,000, Scale $200,000, Custom none. At the cap,
  "API usage pauses until 00:00 UTC on the first day of the next month": HTTP 429,
  `error_code: enforced_spend_limit_reached`, no `retry-after` header.
- A spend limit you set yourself (Billing page) returns HTTP 400 `invalid_request_error`
  ("You have reached your specified API usage limits"). A Claude Code workspace limit
  can return 429 with `retry-after`.
- Algorithm: token bucket, "continuously replenished up to your maximum limit, rather
  than being reset at fixed intervals". 60 RPM may be enforced as 1 request per second;
  short bursts can trigger 429. Limits are maximums, not guaranteed minimums.
- Measured per model class in RPM, ITPM (input tokens/min) and OTPM (output tokens/min).
  - ITPM counts `input_tokens` and `cache_creation_input_tokens`; `cache_read_input_tokens`
    do NOT count (except Haiku 3.5). Caching therefore raises effective throughput.
  - OTPM counts tokens actually generated; `max_tokens` does not count.
  - `inference_geo` "us" and "global" share one pool.
- Per-model limits (RPM / ITPM / OTPM):

| Model | Start | Build | Scale |
|---|---|---|---|
| Fable 5.x (one combined limit; Mythos 5.x share another) | 1,000 / 500k / 100k | 2,000 / 1.5M / 300k | 4,000 / 4M / 800k |
| Opus 5.5, Opus 5, Opus 4.x, Sonnet 5.5, Sonnet 5, Sonnet 4.x, Haiku 5.5, Haiku 4.5 | 1,000 / 2M / 400k | 5,000 / 5M / 1M | 10,000 / 10M / 2M |
| Haiku 3.5 (retired except Google managed) | 1,000 / 100k / 20k | 2,000 / 200k / 40k | 4,000 / 400k / 80k |

- Message Batches: RPM 1,000 / 2,000 / 4,000; requests in processing queue 200k / 300k /
  500k; 100,000 requests per batch (Start / Build / Scale).
- Token counting endpoint: free, 5,000 / 10,000 / 20,000 RPM, separate from messages.
- Managed Agents: 300 create and 1,200 read requests/min per organization.
- Fast mode (Opus 5.5 / 5 / 4.8) has its own limits.
- Workspaces: no spend limit on the default workspace; unset workspace limits equal the
  organization's; organization limits always apply.
- Acceleration limits: a "sharp increase in usage" can return 429; no numbers published.
- 429: wait `retry-after` seconds. Headers `anthropic-ratelimit-{requests,tokens,
  input-tokens,output-tokens}-{limit,remaining,reset}`; `tokens-*` shows the most
  restrictive limit in effect. Higher limits: "Request tier increase" on
  https://platform.claude.com/usage/limits.

## Errors

Source: https://platform.claude.com/docs/en/api/errors

- 413 `request_too_large`: Messages 128 MB, Token Counting 128 MB, Batch 256 MB, Files 500 MB.
- 429 `rate_limit_error`; 500 `api_error` (retry with exponential backoff); 529
  `overloaded_error`. SDKs retry transient failures twice by default, honoring
  `retry-after`.
- Use streaming or batches for requests that may run over 10 minutes.

## Message Batches

Source: https://platform.claude.com/docs/en/build-with-claude/batch-processing

- "All usage is charged at 50 percent of the standard API prices."
- Most batches finish within 1 hour; results after all complete or 24 hours; batches
  expire after 24 hours; results kept 29 days.
- Up to 100,000 requests or 256 MB per batch. No `stream`, fast mode, `fallbacks` or
  `max_tokens: 0`. Cache hits inside batches are best effort. Batches may go slightly
  over a spend limit.

## Prompt caching

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

- Price multipliers of base input: 5-minute write 1.25x, 1-hour write 2x, read 0.1x
  (0.05x on Opus 5.5 and Sonnet 5.5; 0.025x on Fable 5.1 and Mythos 5.1). They stack
  with batch, long-context, data-residency and fast-mode modifiers.
- TTL 5 minutes by default, refreshed free on every hit, measured from the start of the
  request. 1 hour with `"cache_control": {"type": "ephemeral", "ttl": "1h"}`; longer TTL
  entries must come before shorter ones. No manual clear.
- Minimum cacheable length (shorter prompts are silently not cached): 512 tokens (Fable
  5.1, Mythos 5.1, Opus 5.5, Opus 5, Sonnet 5.5, Fable 5, Mythos 5, Haiku 5.5); 1,024
  (Opus 4.8, Sonnet 5, Sonnet 4.6, Sonnet 4.5); 2,048 (Opus 4.7, Mythos Preview); 4,096
  (Opus 4.6, Opus 4.5, Haiku 4.5).
- Up to 4 breakpoints; each looks back at most 20 positions. Breakpoints are free.
  Automatic caching: one top-level `"cache_control": {"type": "ephemeral"}`.
- Invalidation follows tools → system → messages; a change invalidates its level and
  everything after it:
  - tool definitions: everything;
  - web search / citations / speed toggle: system and messages;
  - tool choice, images added or removed: messages;
  - thinking parameters or effort (other than the model default): messages (tools and
    system depend on the model);
  - dropped thinking blocks (Claude 5.1+): everything.
- Caches are per workspace (Claude API, AWS platform, Foundry) or per organization
  (Bedrock, Google). Cached tokens still occupy the context window.

## Thinking and effort

Sources: https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost,
https://platform.claude.com/docs/en/build-with-claude/effort

- Thinking tokens are billed as output, are part of `max_tokens` and count toward rate
  limits. The `display` setting ("omitted" default on Claude 5+, "summarized" earlier)
  changes only what you see, not the bill. Cost is in
  `usage.output_tokens_details.thinking_tokens`; `output_tokens` is the billed total.
- Preserved thinking blocks (Opus 4.5+, Sonnet 4.6+, Haiku 5.5, Fable/Mythos 5.x) count
  toward the context window.
- `max_tokens` is the hard cap on thinking plus answer; effort is soft guidance.
- Manual `budget_tokens`: deprecated on Opus/Sonnet 4.6, rejected on Claude 4.7+;
  minimum 1,024; a target, not a cap; changing it invalidates the cache.
- Claude 5+ models always think (adaptive). Opus 4.6-4.8 and Sonnet 4.6 think only with
  `thinking: {type: "adaptive"}`.
- Effort `output_config.effort`: `low`, `medium`, `high`, `xhigh`, `max` (availability
  varies). Default `high`; `medium` on Opus 5.5 and Haiku 5.5. A behavioral signal, not
  a budget; affects thinking, output and tool calls.

## Context windows and output

Sources: https://platform.claude.com/docs/en/build-with-claude/context-windows,
https://platform.claude.com/docs/en/about-claude/pricing

- 1M tokens at standard pricing for Claude 4.6 and later (Fable, Mythos, Opus 5.5/5/4.8/
  4.7/4.6, Sonnet 5.5/5/4.6, Haiku 5.5); 200k for others. "A 900k-token request is billed
  at the same per-token rate as a 9k-token request." Exception: Haiku 5.5 prompts over
  100,000 tokens (cache reads and writes included) pay the higher price row.
- Up to 128k output tokens per request; 300k with the `output-300k-2026-03-24` beta in
  batches for the newest models. Up to 600 images or PDF pages (100 on 200k models).
- Claude 4.7+ uses a newer tokenizer: about 30% more tokens for the same text. Recount
  with the token counting endpoint for the target model.

## Prices (USD per million tokens)

Source: https://platform.claude.com/docs/en/about-claude/pricing (matches claude.com/pricing)

| Model | Input | 5m write | 1h write | Cache hit | Output | Batch in / out |
|---|---|---|---|---|---|---|
| Fable 5.1 | 10 | 12.50 | 20 | 0.25 | 50 | 5 / 25 |
| Fable 5 | 10 | 12.50 | 20 | 1 | 50 | 5 / 25 |
| Opus 5.5 | 4 | 5 | 8 | 0.20 | 20 | 2 / 10 |
| Opus 5, 4.8, 4.7, 4.6, 4.5 | 5 | 6.25 | 10 | 0.50 | 25 | 2.50 / 12.50 |
| Sonnet 5.5 | 2 | 2.50 | 4 | 0.10 | 10 | 1 / 5 |
| Sonnet 5 | 2 | 2.50 | 4 | 0.20 | 10 | 1 / 5 |
| Sonnet 4.6, 4.5 | 3 | 3.75 | 6 | 0.30 | 15 | 1.50 / 7.50 |
| Haiku 5.5 (prompt ≤ 100k) | 0.10 | 0.125 | 0.20 | 0.01 | 0.50 | 0.05 / 0.25 |
| Haiku 5.5 (prompt > 100k) | 0.50 | 0.625 | 1 | 0.05 | 2.50 | 0.25 / 1.25 |
| Haiku 4.5 | 1 | 1.25 | 2 | 0.10 | 5 | 0.50 / 2.50 |

Other pricing rules:
- US-only inference (`inference_geo`) on Claude 4.6+: 1.1x on all token prices.
- Fast mode: Opus 5.5 $8 / $40; Opus 5 and 4.8 $10 / $50; not available in batches.
- Web search $10 per 1,000 searches plus tokens; web fetch only tokens.
- Code execution: free with web search / web fetch (2026-02-09 versions or later);
  otherwise billed by time. Free hours conflict between pages (1,550 per month vs. 50 per
  day): unresolved.
- Tool definitions, `tool_use` and `tool_result` count as input; tool use adds a system
  prompt overhead (e.g. 286 tokens on Opus 5.5); bash tool 325 tokens, text editor 974
  (Claude 4.7+).
- Managed Agents: $0.08 per running session-hour plus tokens; no batch discount.
- Priority Tier is legacy (no new commitments) and not supported on the Claude 5 models.

## Official recommendations

- Pick the model per task: "Haiku for simple tasks, Sonnet for most production
  workloads, and Opus for the most complex reasoning" (pricing page). Models overview:
  start with Opus 5.5; use Fable 5.1 for demanding reasoning and long-horizon agents.
- Cache repeated context; put static content first and the breakpoint on the last block
  that stays identical; keep thinking and effort settings fixed within a conversation;
  check hit rates with cache diagnostics and on https://platform.claude.com/usage.
- Use the Batch API for work that is not time sensitive; for batches with a shared
  prefix, warm a 1-hour cache with one request first.
- Use `low` / `medium` effort "liberally as your primary control for token cost and
  response time wherever your evals show quality holds"; lower effort before prompting
  Claude to think less; reserve `max` for frontier problems.
- Latency: ask for shorter answers (in sentences or paragraphs, not word counts), set
  `max_tokens`, stream, use `display: "omitted"` for faster first text, use Haiku 5.5
  for speed.
- Ramp traffic gradually to avoid acceleration limits.
