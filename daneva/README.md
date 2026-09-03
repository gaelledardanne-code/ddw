# Daneva — Personal Hustle Planner

Daneva turns big ambitions into daily progress:

```
Vision → Goal → Milestone → Task → Daily Action → Progress
```

v1 is the foundation: goals, milestones, tasks, habits, daily plans, a
deterministic XP/achievement system, and a REST API. It intentionally does
**not** include a smart recommendation engine yet — see "Future Vision"
below.

This project is also a deliberate TDD exercise: every behaviour is built
test-first. See [`PLAN.md`](./PLAN.md) for the architecture and the
incremental slice-by-slice roadmap.

## Architecture

```
app/
  api/          FastAPI routers — HTTP in/out only, no business rules
  services/     Use-case orchestration (repository + domain calls)
  domain/       Pure Python business rules — no FastAPI, no SQLAlchemy, no I/O
  repositories/ DB access, translates between ORM models and domain entities
  models/       SQLAlchemy ORM table definitions
  schemas/      Pydantic request/response models for the API
  db/           Engine/session setup
tests/
  unit/         Fast domain-logic tests (the bulk of the suite)
  integration/  Real-SQLite repository tests
  api/          FastAPI TestClient tests
```

The domain layer has no framework dependencies, so business rules (goal
progress %, XP, streaks, daily-plan totals) are unit tested directly,
without spinning up a server or a database.

## Install

Requires Python 3.12+.

```bash
cd daneva
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

(Available once the API layer exists — see `PLAN.md` for slice order.)

## Run tests

```bash
pytest                      # full suite with coverage
pytest tests/unit           # domain unit tests only
pytest -k goal_creation      # a specific slice
ruff check app tests        # lint
mypy app                    # type-check
```

## How TDD is used here

Every slice of behaviour is built in this order:

1. Write down the expected behaviour.
2. Write the test(s) first.
3. Run pytest — confirm it fails for the right reason (missing code, not a
   typo).
4. Implement the minimum code to pass.
5. Run pytest again — confirm green.
6. Refactor while keeping tests green (this is also where `ruff`/`mypy`
   findings get fixed).

See `PLAN.md` for the full ordered list of slices and their current status.

## API overview (target shape, built incrementally)

```
GET    /goals
POST   /goals
GET    /goals/{id}
PATCH  /goals/{id}
DELETE /goals/{id}
GET    /goals/{id}/progress
POST   /goals/{id}/milestones
POST   /milestones/{id}/tasks
GET    /tasks
PATCH  /tasks/{id}
POST   /tasks/{id}/complete
POST   /habits
GET    /habits
POST   /habits/{id}/complete
GET    /daily-plans/{date}
POST   /daily-plans/{date}/tasks
GET    /stats
```

## Future vision (not built in v1)

Smart/energy-aware daily planning, goal dependencies, recurring tasks,
weekly reviews, productivity analytics, levels, "quests", time blocking,
calendar integration, and natural-language commands (e.g. "I have 2 hours
today, what should I work on?"). The layering above exists specifically so
these can be added later without reworking the foundation.
