# PLAN.md — Daneva: Personal Hustle Planner

> **Status:** all 16 slices below are built — domain, persistence,
> services, and the full REST API, each done test-first. 268 tests,
> 100% coverage on domain/services, ruff/mypy clean. See the git log on
> `claude/daneva-hustle-planner-3mg6vf` for the slice-by-slice history.
> What's next is genuinely new work: the "Future vision" items in the
> README, none of which are built yet.

## 1. What this is

Daneva turns long-term ambitions into daily action:

```
Vision → Goal → Milestone → Task → Daily Action → Progress
```

v1 builds the foundations only: goals, milestones, tasks, habits, daily
plans, a deterministic XP/achievement system, and a REST API over all of
it. No recommendation engine, no "what should I do today" intelligence —
that is explicitly future work (see README "Future Vision").

## 2. Architecture

Layered, and each layer only depends on the layers below it:

```
api/          FastAPI routers. HTTP in, HTTP out. No business rules here.
services/     Orchestrates repositories + domain logic for one use case.
domain/       Pure Python. Entities, enums, and business rules
              (progress %, XP, streaks). No FastAPI, no SQLAlchemy, no I/O.
repositories/ Translates between SQLAlchemy models and domain entities.
              All DB queries live here.
models/       SQLAlchemy ORM table definitions.
schemas/      Pydantic request/response models for the API.
db/           Engine/session setup, Base, dependency-injected DB session.
```

Why this shape:

- **domain/ is dependency-free** so the hardest, most important logic
  (goal completion %, XP awarding, streak calculation, daily-plan
  aggregates) can be unit tested with plain function calls — no DB, no
  HTTP client, no fixtures beyond plain objects. This is where most of
  the test suite lives, and where TDD is easiest to *see*.
- **repositories/ isolate persistence** so integration tests exercise real
  SQLite behavior (constraints, cascades, relationships) without leaking
  ORM concerns into domain rules.
- **services/ is thin glue**: given a repository and some input, call the
  right domain function and persist the result. Mostly tested indirectly
  through API tests, plus a few direct unit tests where orchestration
  itself has logic worth covering (e.g. "completing a task twice does not
  double-award XP" touches both domain and repository).
- **api/ has (almost) no logic**: validate the shape of the request via
  Pydantic, call a service, map the result to a response schema.

This mirrors the standard test pyramid: many fast domain unit tests, a
smaller number of repository/integration tests, fewer API tests, and no
end-to-end tests unless something genuinely can't be verified otherwise.

## 3. TDD workflow used throughout

For every slice below, the same loop applies:

1. Write down the expected behaviour in plain language.
2. Write the test(s) for it first.
3. Run pytest, confirm it fails for the *right* reason (missing
   code/import, not a typo).
4. Write the minimum implementation to pass.
5. Run pytest again, confirm green.
6. Refactor if useful, keeping tests green throughout.
7. Report: behaviour added, tests written, initial failure, what made it
   pass, what was refactored.

Slices are vertical and small. A slice is not "done" until its tests
pass; the next slice does not start until the previous one is confirmed.

## 4. Incremental slices

Each slice is a separate, reviewable step. Order matters: later slices
depend on entities/rules introduced earlier.

1. **Goal creation** (domain) — `Goal` entity, enums for category/
   priority/status, validation rules (title required, sensible defaults,
   `created_date` auto-set).
2. **Goal lifecycle** (domain) — pause/resume/complete/abandon
   transitions and which transitions are illegal.
3. **Milestones & Tasks** (domain) — entities, task status/priority/
   energy-level enums, task belongs to a goal directly or via a
   milestone.
4. **Goal progress** (domain) — `completed / total * 100` over a goal's
   tasks, including zero-task goals, cancelled tasks, and tasks spread
   across multiple milestones.
5. **XP** (domain) — deterministic XP per task priority, and the rule
   that completing an already-completed task never re-awards XP.
6. **Habits & streaks** (domain) — completions, streak calculation,
   broken streaks, same-day duplicate completion, 7-day streak
   achievement trigger.
7. **Achievements** (domain) — First Task, 100 XP, 7 Day Streak, First
   Goal Completed, evaluated from state rather than stored as mutable
   flags.
8. **Daily plans** (domain) — add/remove tasks, mark complete,
   completion %, total estimated minutes, total XP.
9. **Persistence** (db/models/repositories) — SQLAlchemy models and
   repositories for everything above, with integration tests against a
   real (file-based test) SQLite DB, including relationships/cascades.
10. **Services** — use-case orchestration wiring domain + repositories
    together (e.g. `complete_task` = repository fetch → domain XP calc →
    repository save, idempotently).
11. **API — Goals** — `GET/POST /goals`, `GET/PATCH/DELETE /goals/{id}`,
    `GET /goals/{id}/progress`.
12. **API — Milestones & Tasks** — `POST /goals/{id}/milestones`,
    `POST /milestones/{id}/tasks`, `GET /tasks`, `PATCH /tasks/{id}`,
    `POST /tasks/{id}/complete`.
13. **API — Habits** — `POST/GET /habits`, `POST /habits/{id}/complete`.
14. **API — Daily plans** — `GET /daily-plans/{date}`,
    `POST /daily-plans/{date}/tasks`, remove/complete endpoints.
15. **API — Stats** — `GET /stats` (totals: XP, goals, tasks, streaks,
    achievements unlocked).
16. **Validation & error handling pass** — invalid input, 404s, 409s for
    illegal state transitions, consistent error schema, tests for all of
    it.

Quality tooling (pytest-cov, Ruff, mypy) is configured once, in step 0,
before slice 1, so every subsequent slice is checked against it rather
than retrofitted later.

## 5. Explicitly out of scope for v1

- Smart/automatic daily task selection ("what should I focus on today").
- Energy-aware or dependency-aware planning.
- Recurring tasks, calendar integration, time blocking.
- Weekly reviews, analytics beyond basic `/stats`.
- Natural-language commands.

The layering above (domain isolated from persistence and transport) is
chosen specifically so these can be added later without rewriting the
foundation — e.g. a future recommendation engine would be a new
`services/planning.py` that reads existing domain/repository data, not a
change to how goals/tasks/XP work.
