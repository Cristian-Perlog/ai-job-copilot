# AI Job Application Copilot

## Summary

**AI Job Application Copilot** is a job-application tracker for early-career software engineers.

Its one differentiator: **you never type an application.** Paste a job URL or the posting text and it's captured — an LLM extracts the company, role, location, tech stack, and salary into a draft you confirm in one click. Everything else is a focused, well-built tracker around that capture core.

This project has a deliberate dual goal, with both halves treated as equal priority:

1. **A real product** that an early-career engineer would actually use during a job search.
2. **A production-grade engineering learning project** — backend design, auth, data modeling, CI, observability, and cloud deployment done the way a strong team would do them.

When the two goals conflict, the rule is: **product decisions favor the wedge** (lower-friction capture, a tracker that earns daily use). **Engineering decisions may favor learning value when the cost is small** (e.g. choosing a slightly more involved pattern because it's worth practicing), but never at the expense of the product feeling worse to use.

---

## Motivation

Job hunting as a student or early-career developer is fragmented and tedious:

* Job links live in bookmarks, tabs, and random notes.
* Applications get tracked in a spreadsheet — or not at all.
* The boring part isn't *deciding* to apply; it's the **data entry** of copying company, role, location, stack, and salary out of a posting and into a row.

That data-entry tax is exactly why most trackers lose to a spreadsheet: a spreadsheet is already open and asks nothing of you. So the wedge is not "more features." It's **removing the typing**: capture an application from a URL or pasted text in seconds, with no manual entry.

---

## Target Users

### Primary users

* Computer Science students nearing graduation.
* Early-career software engineers actively job hunting.
* Developers applying for internships or first full-time roles.

These users apply to many roles in a short, intense window and feel the data-entry tax acutely.

### Secondary users (future)

* Career switchers into tech.
* Bootcamp graduates.

---

## Positioning

### The landscape

The space is crowded: **Huntr**, **Teal**, **Simplify**, **Careerflow**, and a long tail of free **Notion / Google Sheets templates**. Most compete on breadth — resume builders, AI cover letters, contact CRMs, Chrome autofill, job boards. The free templates compete on being free and instantly editable.

### The wedge (one sentence)

> The only tracker where you never type an application — paste a URL or the posting text and it's captured.

Competitors treat capture as a checkbox feature behind a browser extension. Here it *is* the product. We win on getting an application into the tracker faster and with less effort than anyone else, then being a clean, trustworthy home for it.

### Why not a spreadsheet?

A spreadsheet is the honest competitor, and it's a strong one: it's already open, it's free, it's infinitely flexible, and it never makes you log in. Most trackers lose to it because they add features the user didn't ask for while still making them type every field.

We don't try to out-feature a spreadsheet — we beat it on **friction**. Pasting a link and confirming a pre-filled draft is less work than tabbing to a sheet and typing five columns. If we are ever *more* work than a spreadsheet for the core loop of "I found a job, save it," we have lost. Every product decision is measured against that bar.

---

## Product Vision

The committed vision is deliberately narrow: **frictionless capture + a tracker that does the core job excellently.** Two pillars, done well, beat five pillars done partially.

1. **AI-first capture**
   Paste a job URL or posting text; an LLM extracts company, role, location, tech stack, and salary into a *draft* application. The user reviews and confirms — extraction is assistive, never silently authoritative.

2. **Application & interview tracking**
   A clean home for every opportunity: statuses, interviews, notes, and a dashboard that makes the pipeline legible at a glance. Import from an existing spreadsheet, export your data whenever you want.

Anything outside these two pillars is explicitly **not** in the committed vision and lives under "Future Ideas" below until the core is excellent.

---

## North-Star Metric

**Median applications captured per active user in week 1.**

This metric only moves if capture is genuinely frictionless — it's resistant to vanity features and directly measures whether the wedge is working. If users aren't capturing applications easily in their first week, nothing else matters. In the MVP phase, before capture (Phase 2) is implemented and the product is deployed, the same metric is measured over manual application creation and CSV imports. This manual + CSV proxy is a **weaker signal** than the true capture metric — it tracks whether people will track applications at all, not whether the friction-removing wedge works — so it is an interim stand-in, not an equivalent.

---

## MVP Scope (Phase 1)

The MVP is a useful daily tracker that a real job-seeker could adopt — *before* any AI is added. Capture (the wedge) lands in Phase 2; the MVP must stand on its own as the best-feeling manual tracker, with a clean migration path in and out.

### Authentication

* Sign in with Google (Google ID token exchanged for a backend-minted, httpOnly session).
* Secure, per-user data isolation.

### Job application tracking

Create, edit, and delete applications, each storing:

* company, role, location, job link
* tech stack / tags
* salary (if known)
* notes
* status

Statuses: **Wishlist, Applied, Interviewing, Offer, Rejected.** Status changes are recorded as history so the pipeline timeline is real, not a single mutable field. The allowed transitions between statuses are defined in [docs/architecture.md](./architecture.md).

### Interview tracking

Add interviews linked to an application, storing date, type (phone / online / onsite), and prep notes.

### Dashboard (command center)

A pipeline-oriented overview: applications by status, upcoming interviews, and applications awaiting a response.

**Designed empty state.** A brand-new user must never see a dead "0 / 0 / 0 / 0" dashboard. The first-run experience guides them to create or import their first application — the empty state is a designed onboarding surface, not an afterthought.

### Data portability

* **CSV import** — a one-step migration path off an existing spreadsheet. This both lowers adoption friction and exercises a real parsing/validation flow.
* **CSV / JSON export** — users can take their data out at any time. This is a trust feature: a tracker you can't leave is one you won't commit to.

---

## Phase 2 — Capture Wedge (first AI feature)

The flagship AI feature, and the first one built:

### Paste-to-capture

* The user pastes a **job URL** or **posting text**.
* An LLM extracts company, role, location, tech stack, and salary.
* The result is a **draft** application with a required **confirm step** — the user verifies and edits before it's saved. Extraction is fallible; the human stays in the loop.

This replaces manual entry as the primary way applications enter the system and is the single feature most likely to move the north-star metric.

Operational guardrails ship **with** this first AI endpoint, not later: per-user rate limits and quotas, plus an audit trail of generations (cost and usage are real concerns from the first AI call).

---

## Pricing & Retention (open question, honest default)

Job search is **episodic**. A user's search lasts weeks to a few months, and the best outcome — they get hired — means they *stop needing the product*. **Users churn on success, by design.** That breaks the assumptions behind a perpetual monthly subscription.

The honest default, recorded as the working position until evidence says otherwise:

> Price around the **active-search period** (e.g. a time-boxed plan covering an active search) rather than an open-ended subscription that quietly bills people who already got the job.

This is an **open question**, not a settled decision — but the default direction is "don't pretend job search is forever."

---

## Future Ideas (explicitly not committed)

These are noted so they aren't reinvented later. None are part of the committed vision; the bar for promoting any of them is "the capture + tracking core is already excellent."

* **Prioritization / scoring of jobs.** Only valuable if applied to *inbound or un-curated* jobs (e.g. a recommendation feed). Scoring jobs the user *already chose to save* just restates their own inputs and adds no information — so this is out unless there's an un-curated job stream to score.
* **Interview Prep Hub** — structured, AI-assisted interview preparation.
* **AI Job Coach** — cover-letter generation, tailored interview questions, application feedback.
* **Integrations** — LeetCode progress, calendar sync for interviews.
* **Email/inbox parsing (deferred indefinitely).** Auto-capturing applications from Gmail is tempting, but the restricted Gmail OAuth scopes it requires trigger Google's CASA security-audit process — a recurring, expensive compliance burden that is impractical for a solo developer. URL/text paste delivers most of the value and sidesteps that wall entirely.

---

## Long-Term Vision

Build a realistic, end-to-end SaaS that is genuinely good at one thing — getting job applications captured and tracked with the least possible friction — while serving as a portfolio-grade demonstration of production engineering: API design, data modeling, authentication and security, testing, CI/CD, observability, infrastructure-as-code, and a documented cloud deployment.

The measure of success is both halves of the dual goal: a product an early-career engineer would actually keep open during a job hunt, and a codebase a strong engineering team would respect.
