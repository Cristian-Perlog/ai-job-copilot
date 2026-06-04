# ADR-0004: Hybrid deployment — build for AWS, run cheap

## Status

Accepted.

## Context

This is a portfolio-grade project with two goals: demonstrate real
infrastructure-as-code and cloud-deployment skill, **and** run a public demo
without paying idle rent. An always-on AWS stack (ECS Fargate + RDS + ElastiCache
+ ALB + NAT) idles at roughly **$130–190/month with zero users** — not justifiable
for a demo. But "never touch AWS" forfeits the learning value. The value is in
**building** the IaC and doing **one** real deploy, not in keeping it running.

## Decision

Build AWS-ready, deploy to AWS **once** as a documented exercise, then run
day-to-day on cheap PaaS.

**AWS learning exercise**

- Terraform under `infrastructure/`.
- ECR + ECS (EC2 launch type, e.g. `t4g.small`, or App Runner — cheaper than
  Fargate here), RDS Postgres.
- **No ElastiCache, no NAT** (public subnets / default VPC for the exercise).
- **AWS Budgets alarms at $10 / $25 / $50 set BEFORE any `apply`.**
- `terraform destroy` after documenting it.

**Day-to-day hosting**

- **Vercel** (frontend) + **Fly.io / Railway** (backend container) + **Neon**
  (Postgres, with point-in-time recovery).

**Migration rule (both targets):** migrations run as an **explicit deploy step
before** the new app version goes live — **never on container start**. Once live,
schema changes follow the **expand/contract** pattern.

## Alternatives considered

- **Always-on ECS Fargate + RDS + ElastiCache + ALB + NAT.** Rejected: ~$130–190
  /month idle for a demo with no users. The learning is in building and one real
  deploy, not in the standing bill.
- **PaaS only, never touch AWS.** Rejected: forfeits the IaC / cloud-deploy
  learning that is half the point of the project.

## Consequences

- The codebase stays cloud-portable: containerized, config via env vars, no
  hard dependency on a single provider's primitives.
- One real, documented AWS deploy proves the skill; budget alarms cap the
  blast radius; `destroy` ends the bill.
- Day-to-day cost is near-zero on PaaS free/cheap tiers.
- Running migrations as a pre-deploy step (not on start) avoids races between
  multiple booting containers and keeps rollouts safe.
