# AGENTS.md - Backend (`app/server`)

**Parent:** [/AGENTS.md](../../AGENTS.md). Read it first. Universal rules -
money handling, UTC, secrets, dependencies, commits, definition of done - live
there and are not repeated here.

**Scope of this file:** the FastAPI service. Stack, the layered architecture and
its dependency rule, error handling, configuration, and the commands that verify
a backend change.

**Do not read `app/client/**` while implementing a backend story.** The backend
owns the API contract; it does not adapt to the frontend's internals.

---

## 1. Stack

- **Python 3.11+**, **FastAPI**, **Uvicorn**.
- **Poetry** for dependency management. `pyproject.toml` and `poetry.lock` are
  the source of truth - never `pip install` into the environment and leave the
  lockfile behind.
- **pytest** (with `httpx` for API-level tests).
- Persistence is currently **in-memory**. PostgreSQL is the target; see §6.

---

## 2. Layered architecture

This is the single most important rule in this layer. The full rationale is in
[docs/presentation-domain-data.md](docs/presentation-domain-data.md) - read it
before changing anything structural.

```
Presentation  ->  Service/Application  ->  Domain  <-  Data
```

**Dependencies point inward. The domain is the centre and imports nothing from
the layers around it.**

| Layer | Directory | Owns |
|---|---|---|
| Presentation | `app/api/`, `app/api_contracts/`, `app/dependencies.py` | HTTP routes, DTOs, status codes, dependency wiring |
| Application | `app/service/` | Use cases, workflow coordination, transaction boundaries |
| Domain | `app/domain/` | Entities, business rules, domain errors, repository protocols |
| Data | `app/data/` | Repository implementations, ORM models, persistence details |
| AI | `app/agents/` | LangChain/LangGraph research workflows (Phase 3) |

Each of those directories has its own `AGENTS.md` with the rules for working
inside it. Read the one for the directory you are editing.

### The dependency rule, concretely

- `app/domain/` must not import FastAPI, Pydantic API contracts, SQLAlchemy,
  HTTP clients, LangChain, or anything from `app/data/`, `app/service/`, or
  `app/api/`.
- `app/service/` may import from `app/domain/`. It must not import FastAPI,
  `app/api_contracts/`, or a concrete repository from `app/data/`.
- `app/api/` may import from `app/service/`, `app/api_contracts/`, and
  `app/domain/` (for error types). It must not contain business rules or
  persistence code.
- `app/data/` implements protocols declared in `app/domain/repositories.py`. The
  domain never imports it back.

If a change seems to require breaking this, it is almost always a sign that
logic is being written in the wrong layer. Move the logic, do not break the
rule. If you genuinely believe the rule is wrong for a case, stop and raise it
rather than quietly routing around it.

### Where does my code go?

| If you are writing... | It goes in |
|---|---|
| A rule that is true regardless of API or database | `app/domain/` |
| Coordination across several entities or repositories | `app/service/` |
| A URL, status code, or request/response shape | `app/api/` + `app/api_contracts/` |
| A query, session, or storage mapping | `app/data/` |
| An LLM prompt, tool, or agent graph | `app/agents/` |

---

## 3. Structure

```
app/server/
├── app/
│   ├── main.py              FastAPI app setup, middleware, router registration
│   ├── dependencies.py      Dependency injection wiring
│   ├── api/                 -> app/api/AGENTS.md
│   ├── api_contracts/       -> app/api_contracts/AGENTS.md
│   ├── service/             -> app/service/AGENTS.md
│   ├── domain/              -> app/domain/AGENTS.md
│   ├── data/                -> app/data/AGENTS.md
│   └── agents/              -> app/agents/AGENTS.md
├── tests/                   -> tests/AGENTS.md
├── docs/
│   └── presentation-domain-data.md
├── pyproject.toml
└── Dockerfile
```

`main.py` stays thin: app construction, middleware, lifespan, router
registration. No routes, no business logic.

---

## 4. Conventions

### Async

The service and repository layers are `async` end to end, so a real database
driver can drop in without a rewrite. Do not add blocking I/O inside an `async`
function - it stalls the event loop for every concurrent request. If a library
is sync-only, isolate it in `app/data/` and run it in a thread executor.

### Typing

- Type every function signature, including returns. Use modern syntax:
  `str | None`, `list[Holding]`, not `Optional[str]` or `List[Holding]`.
- Repository interfaces are `typing.Protocol`, structural not inherited.
- Domain entities are `@dataclass`. Pydantic models belong to
  `app/api_contracts/` only.

### Errors

- Business failures raise **domain exceptions** from `app/domain/models.py`
  (`OversellError`, `HoldingNotFoundError`, ...). They carry no HTTP meaning.
- Only `app/api/` converts a domain exception into an `HTTPException` with a
  status code. Never raise `HTTPException` from a service, domain, or data
  module.
- "Not found" as a normal outcome is `None` from the service; the route turns it
  into a 404. Reserve exceptions for rule violations.

### Naming

- `api_contracts/<context>.py` for DTOs, suffixed `Request` / `Response`.
- `service/<context>_service.py` for use cases.
- `domain/models.py` for entities, `domain/repositories.py` for protocols.
- `data/<backing>_<context>_repositories.py` for implementations.

### Configuration

Typed settings, loaded once, injected. No `os.environ` reads scattered through
business logic and no environment-name branching - select an implementation by
configuration, per the parent file's provider rule.

### API design

- Routes are path-scoped by owner: `/users/{user_id}/portfolio/...`.
- Plural resource nouns, no verbs in paths.
- `201` on create with the created resource, `204` on delete with no body,
  `409` on a state conflict, `422` for validation (FastAPI does this for you).
- Adding a field is backward compatible. Renaming or removing one is a breaking
  change and must be coordinated with the client in a single commit.

---

## 5. Verification

```bash
cd app/server && poetry run pytest
```

Run from `app/server`. The container image targets Python 3.14 and `pyproject.toml`
requires `>=3.11`; if the host Python is older, run inside the dev container
instead:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend pytest
```

For an API change, also exercise it live. `make dev` from the repository root,
then interactive docs at `http://localhost:8000/docs` and health at
`http://localhost:8000/health`.

Every financial calculation change needs a test with a hand-computed expected
value. Do not assert against whatever the code currently returns - that tests
nothing.

---

## 6. Not yet in scope

Do not introduce these without a story that explicitly calls for them. Each one
adds infrastructure and a bounded context, and the portfolio model is not stable
enough to absorb them:

- Authentication and a users table (`user_id` is currently an unvalidated path
  parameter - this is known and deliberate).
- SQLAlchemy, Alembic migrations, PostgreSQL wiring.
- Market data providers (`yfinance` or otherwise), background price refresh.
- WebSocket streaming, technical indicator services, trading signals.

When persistence lands: ORM models go in `app/data/`, never in `app/domain/` or
`app/api_contracts/`, and the existing repository protocols must not change
shape to accommodate the driver.
