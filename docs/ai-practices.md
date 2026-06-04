# AI Practices

Decisions for the AI features, recorded **now** so the first one ships right.
Nothing here is implemented yet — the capture wedge is the first AI feature
(Phase 2, see [roadmap.md](./roadmap.md)). This is a reference, not a tutorial:
when paste-to-capture is built, it must follow these rules.

The first AI feature is **extraction**: paste a job URL or posting text → an LLM
returns a *draft* application (company, role, location, tech stack, salary) that
the user confirms before save. The human stays in the loop; extraction is never
silently authoritative.

---

## Models & cost

- **Model tiering.** Use a **cheap, fast model class** (Haiku-class) for
  extraction — it is a constrained, schema-bound task. Reserve a mid-tier model
  for open-ended *generation* only if such a feature is ever built.
- **Prompt caching.** Cache the stable prefix (system prompt, extraction schema,
  instructions) so only the variable posting text is billed at full rate.
- **Message Batches API** for any bulk, offline, non-interactive work (50%
  discount). Not for the interactive capture path.
- **Streaming** for any interactive generation, so the UI shows progress as
  tokens arrive. Do **not** build a Celery-style poll-a-job-status loop for
  interactive AI — there is no queue in this system (see architecture.md).

## Structured output

- Extraction returns **structured JSON** validated against a **JSON schema**.
- Each extracted field carries a **confidence** signal, and the UX makes the
  draft **user-confirmed**: the user reviews and edits before anything is saved.
- Low confidence surfaces in the UI (flag the field) rather than silently
  dropping or guessing.

## Audit trail — `ai_generations` (mandatory)

A dedicated audit table ships **with the first AI endpoint**, for cost tracking
and reproducibility. Required columns:

| column | purpose |
| --- | --- |
| `id` | PK |
| `user_id` | FK to `users` (cascade on delete) |
| `feature` | which AI feature (e.g. `capture`) |
| `model` | model id used |
| `prompt_version` | version of the prompt template |
| `input_tokens` | billed input tokens |
| `output_tokens` | billed output tokens |
| `cached_tokens` | tokens served from prompt cache |
| `cost_usd` | computed cost |
| `latency_ms` | end-to-end latency |
| `status` | success / error / refused |
| `created_at` | UTC timestamp |

This makes cost real from the first call and lets us reproduce and debug any
generation by prompt version.

## Quotas & rate limits

- **Per-user quotas + rate limits** ship **with** the first AI endpoint, never
  retrofitted. Cost and abuse are real concerns from the first call.

---

## Security

### Prompt-injection trust boundary

- Job-posting text and URLs are **untrusted data**, not instructions. Role-separate
  them: untrusted content goes in a clearly delimited data slot, never the
  instruction channel, and must not be able to redirect the model.
- **No tools, no agency** in v1. The model extracts; it does not act.
- Output is **draft-only with human confirm** — even a successful injection cannot
  silently mutate the user's data.

### SSRF (URL fetching)

When the user pastes a **URL**, fetching it is server-side request forgery
territory. Rules:

- **https only.**
- **Resolve the host and reject private / link-local / loopback / cloud-metadata
  ranges BEFORE connecting** (e.g. `127.0.0.0/8`, `10/8`, `172.16/12`,
  `192.168/16`, `169.254.0.0/16` including `169.254.169.254`, IPv6 equivalents).
- **No following redirects into private ranges** — re-validate every hop.
- **Pin the connection to the validated IP** (or re-validate at connect time);
  never let the HTTP client re-resolve the hostname after validation. This closes
  the DNS-rebinding / TOCTOU gap where a name validated as public re-resolves to a
  private address between the check and the connect.
- Enforce **timeouts**, a **response size cap**, and a **content-type allowlist**
  (HTML/text only).

### PII & data protection

- Resumes, notes, and posting content are **sensitive**. A **vendor DPA** and a
  **retention policy** are documented in the privacy policy before processing
  real user data.
- **Delete / export endpoints** are designed in from Phase 1; `ON DELETE CASCADE`
  on user-owned tables (see architecture.md) makes erasure feasible, including the
  `ai_generations` rows.

---

## Evaluation

- Maintain a **small golden set** of postings with expected extractions.
- Use an **LLM-as-judge rubric** to score extractions against the golden set
  **before** iterating on prompts — measure, then change, so prompt edits are not
  blind. Bump `prompt_version` on every change so results stay attributable.
