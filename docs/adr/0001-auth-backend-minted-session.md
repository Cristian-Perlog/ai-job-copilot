# ADR-0001: Backend-minted session from a Google ID token

## Status

Accepted.

## Context

The product needs Google sign-in and strict per-user data isolation. The frontend
is Next.js; the backend is FastAPI. We must decide **who owns the session** — the
frontend auth stack, or the backend API.

Two pressures shape the choice:

- The API should be independently usable and testable, not coupled to a specific
  frontend auth library.
- Sessions must be XSS-resistant: tokens should never sit in JavaScript-accessible
  storage.

## Decision

The backend mints and owns the session.

1. The frontend uses Google Identity Services to sign the user in and obtain a
   Google **ID token**.
2. It POSTs that token **once** to `POST /api/v1/auth/google`.
3. The backend verifies the token's signature, audience, issuer, and expiry using
   the `google-auth` library, then upserts the user.
4. The backend mints an **opaque, server-side session** (a DB-backed or
   signed session id) and sets it in an **httpOnly + Secure + SameSite=Lax**
   cookie.
5. State-changing routes require a **CSRF double-submit token**.
6. CORS uses `allow_credentials` with a single explicit origin
   (`settings.frontend_origin`, already wired in `main.py`) — never `*`.
7. **Logout** invalidates the server-side session.

**Cookie topology (production same-site via proxy).** ADR-0004 runs the frontend
on Vercel and the backend on Fly.io/Railway — different registrable domains. A
`SameSite=Lax` cookie is **not** sent on cross-site fetch/XHR, so the flow above
would not function if the browser called the backend host directly. Therefore the
**production topology keeps the API same-site** by proxying it through the
frontend's own domain via **Next.js rewrites**: the browser calls
`https://app.example.com/api/...` and Vercel rewrites that to the backend host.
This preserves `SameSite=Lax` (the CSRF double-submit token stays
defense-in-depth, not the sole defense) and removes browser CORS from the
production path entirely. The CORS middleware remains, but only matters for
**local dev**, where the frontend and backend run on different ports.
**Documented fallback:** if the proxy ever becomes a problem, switch the session
cookie to `SameSite=None; Secure` and promote the CSRF token to the **load-bearing**
defense (no longer merely defense-in-depth).

**Session mechanics (pinned).**

- **TTL** — **7-day idle timeout** with a **30-day absolute cap**.
- **Rotation** — the session id is **rotated on every login** (a new session row
  is created and the old one invalidated).
- **Cookie attributes** — **host-only** (no `Domain` attribute) and `Path=/`, in
  addition to httpOnly + Secure + SameSite=Lax.
- **CSRF double-submit mechanics** — a **non-httpOnly `csrf_token` cookie** is set
  alongside the session; the frontend echoes it in an **`X-CSRF-Token` header** on
  every mutating request; the backend requires **`header == cookie`** and ties the
  token to the session.

## Alternatives considered

- **Auth.js / NextAuth owns the session; backend validates Auth.js JWTs.**
  Rejected: it couples the API to the frontend auth stack, makes the backend
  awkward to use or test on its own, and ties session semantics to a JS library's
  conventions. Backend-minted sessions keep the API independent and are the
  clearer portfolio story.

## Consequences

- The backend owns session storage, expiry, and rotation — more backend code, but
  full control over invalidation and a clean logout.
- The frontend never holds a token in JS-accessible storage; the httpOnly cookie
  is XSS-resistant.
- CSRF protection is now our responsibility, handled via the double-submit token
  on mutating routes.
- The API is usable and testable without the Next.js app in the loop.
- Production correctness depends on the **Next.js rewrite proxy** keeping the API
  same-site; this is a deployment-topology commitment, not just an app-code one.
  If that proxy is ever removed, the cookie must move to `SameSite=None; Secure`
  and the CSRF token becomes load-bearing rather than defense-in-depth.
- Browser CORS is **not** on the production request path (same-origin via the
  proxy); the CORS middleware exists for local dev only, where ports differ.
