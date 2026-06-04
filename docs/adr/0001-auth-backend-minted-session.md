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
