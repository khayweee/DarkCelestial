# AGENTS.md - Repository Root

**Scope of this file:** the whole repository. Project purpose, layout, universal
engineering rules, local development, packaging, and deployment.

**This file does not contain client-specific or server-specific rules.** Those
live in the child `AGENTS.md` files listed below.

---

## 1. The harness contract

This repository uses a strict parent-child instruction tree. Every `AGENTS.md`
governs its own directory and everything beneath it that has no closer
`AGENTS.md`.

### The tree

```
AGENTS.md                                  <- you are here (universal)
├── app/client/AGENTS.md                    <- frontend layer
│   └── src/
│       ├── app/AGENTS.md                   <- routes, layouts, server components
│       ├── components/AGENTS.md            <- UI and feature components
│       ├── hooks/AGENTS.md                 <- client-side React hooks
│       └── lib/AGENTS.md                   <- API client, formatting, utilities
└── app/server/AGENTS.md                    <- backend layer
    ├── app/api/AGENTS.md                   <- presentation: FastAPI routers
    ├── app/api_contracts/AGENTS.md         <- presentation: Pydantic DTOs
    ├── app/service/AGENTS.md               <- application: use cases
    ├── app/domain/AGENTS.md                <- domain: entities, rules, protocols
    ├── app/data/AGENTS.md                  <- data: repository implementations
    ├── app/agents/AGENTS.md                <- AI: LangChain/LangGraph research
    └── tests/AGENTS.md                     <- test conventions
```

### Rules for reading

1. **Always read this root file.** It applies to every task.
2. **Read the chain down to your working directory.** Editing
   `app/server/app/service/portfolio_service.py` means reading this file, then
   `app/server/AGENTS.md`, then `app/server/app/service/AGENTS.md`. Nothing else
   is required.
3. **Do not read the sibling layer's tree during implementation.** A backend
   task does not need `app/client/AGENTS.md`.
4. **Cross-layer reading is allowed only during exploration**, and only for
   these reasons:
   - confirming an API contract before changing it,
   - tracing a bug that visibly crosses the HTTP boundary,
   - answering a question that is explicitly about both layers.

   When you read across layers, treat the other layer as **read-only**. Do not
   edit files outside your layer in the same change unless the task explicitly
   asks for a coordinated contract change.

### Rules for writing

1. **Never restate a parent rule in a child file.** If a rule is true for both
   client and server, it belongs here and only here. Duplication is how this
   harness rots.
2. **A child file may narrow a parent rule, never contradict it.** If you
   believe a child needs to contradict the parent, the parent is wrong - fix the
   parent and say so.
3. **Keep each file about its own directory.** If you find yourself writing
   about a different directory, the content belongs in that directory's file.
4. When directory structure or contributor-facing workflow changes, update the
   affected `AGENTS.md` **in the same change**. Stale instructions are worse
   than absent ones.

---

## 2. What this project is

An AI-native **investment portfolio tracker** for individual investors.

Users record what they own and what they traded, then the product explains how
that portfolio is actually performing and where its risk sits.

Delivery phases, in order:

| Phase | Theme                | Capability                                                                                                                                             |
| ----- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1     | Portfolio tracking   | Securities, units, price, broker, transaction fees, cost basis, realized and unrealized PnL                                                            |
| 2     | Performance analysis | Annualised growth rate (CAGR), expected growth, time-weighted and money-weighted returns, benchmark and index comparison, allocation and concentration |
| 3     | Agentic research     | LangChain/LangGraph tooling that explains portfolio exposure, risks, and opportunities in plain language                                               |

Authoritative product and architecture documents - read these before designing
anything non-trivial, and do not duplicate their content into `AGENTS.md` files:

- [docs/product-vision.md](docs/product-vision.md) - scope, phases, target user, open questions.
- [docs/system-architecture.md](docs/system-architecture.md) - dev/prod service topology, AWS targets, provider abstraction, config-driven environments.
- [docs/databaseformultipleusers.md](docs/databaseformultipleusers.md) - multi-user data model direction.
- [app/server/docs/presentation-domain-data.md](app/server/docs/presentation-domain-data.md) - backend layering, in depth.

Work arrives as **epics and stories**. A story tells you the behaviour to build;
this harness tells you the shape it must take. If a story conflicts with a
convention here, say so explicitly before implementing - do not silently pick
one.

---

## 3. Repository layout

```
.
├── app/
│   ├── client/          Next.js frontend (own package.json, own Dockerfile)
│   └── server/          FastAPI backend (own pyproject.toml, own Dockerfile)
├── docs/                Product vision, system architecture, data design
├── .claude/             Claude Code adapter: skills and agents only, no conventions
├── docker-compose.yml       Base service definitions
├── docker-compose.dev.yml   Development overlay (hot reload, bind mounts)
└── Makefile             Entry point for all local orchestration
```

`app/client` and `app/server` are **independent deployables** with independent
dependency manifests. There is no shared code directory and no build-time
coupling between them. They are coupled only by the HTTP contract.

---

## 4. Universal engineering rules

These apply to **both** layers. Layer-specific rules are in the child files.

### Money and correctness

This is a financial application. Wrong numbers are the worst possible defect
class, worse than a crash, because they are silent.

- **Never use binary floating point for monetary amounts, quantities, fees, or
  anything derived from them.** Use `Decimal` on the server and integer minor
  units or a decimal library on the client. Repeated float arithmetic across a
  transaction history accumulates error into a user's reported PnL.
  _Known debt: the current server code uses `float` throughout
  `app/server/app/domain/models.py`. Migrating it is tracked work; do not add
  new float-based money paths._
- **Never round in intermediate calculations.** Round once, at the presentation
  boundary, and state the rounding mode.
- **Every financial formula gets a unit test with a hand-computed expected
  value**, including the boundary cases: zero quantity, full exit, partial sell,
  fees, and a sell that would go negative.
- Cost basis, realized PnL, and unrealized PnL must be **derived from the
  transaction history**, not stored as free-standing mutable numbers that can
  drift out of sync.

### Time and identity

- All timestamps are **timezone-aware UTC**, stored and transported as ISO 8601.
  Trade dates are calendar dates, not timestamps - do not conflate them.
- Convert to a user's local timezone only at the presentation boundary.
- Identifiers are opaque strings (UUIDs). Never expose a database sequence
  number in an API.

### Boundaries and providers

- External services - market data, LLM providers, storage, email - are reached
  **only through an internal interface** owned by this codebase, per
  [docs/system-architecture.md](docs/system-architecture.md). Selecting an
  implementation is a configuration change, never a code change.
- Never scatter `if environment == "prod"` through business logic. Read typed
  configuration instead.

### Code design

SOLID is enforced, not aspirational. The practical consequences:

- **Name every meaningful access.** Reaching into a structure inline hides intent
  and cannot be tested on its own. Wrap it in a named function or a method on the
  owning class:

  ```python
  # no
  fee = data["transaction"]["fee"]

  # yes
  def get_transaction_fee(data: dict) -> Decimal: ...
  ```

  A reader of the call site should know what is being read without opening the
  structure, and the accessor should be unit-testable by itself. This applies
  equally to derived values, formatting, and predicates - if a chunk of inline
  logic needs a comment to explain what it produces, it needs a name instead.

- **When building a feature, work down this ladder and stop at the first rung
  that fits:**
  1. Extend the existing class or module.
  2. Refactor the existing class, when the refactor is itself meaningful and not
     just a way to make room.
  3. Create a new function or class.

  Reach for a new class only when the responsibility is genuinely new. Reach for
  a refactor only when it leaves the code better independent of your feature -
  otherwise you are paying a maintenance cost to avoid extending something.

- A class that needs an `isinstance` check, a type flag, or an `if` on a caller's
  identity to do its job has the wrong shape. Split the responsibility or depend
  on a protocol instead.

### Writing style

Applies to all written output: code, comments, docstrings, documentation, commit
messages, PR descriptions, and handoffs.

- **Never use the em dash character.** Use a plain dash `-` instead.
- **Never use the section sign character.** Write the word `section`, as in
  `section 4`.

### Secrets and user data

- No secrets, API keys, tokens, or real portfolio data in the repository, in
  fixtures, in test data, or in log output.
- Local secrets go in `.env.local` (git-ignored). Everything a new collaborator
  must set is documented in the relevant layer's `AGENTS.md`.
- Never log a full transaction record or holding at info level.

### Dependencies

- Prefer the standard library and what is already installed.
- Adding a dependency needs a one-line justification in the PR: what it does
  that existing tooling cannot. Financial and AI libraries especially - they age
  fast and carry large transitive trees.
- Never add a dependency to work around a convention in this harness.

### Change discipline

- Keep changes scoped to the task. No opportunistic refactors of untouched code
  in a feature change.
- Do not edit generated files, and do not commit build output.
- Do not disable, skip, or loosen a failing test or lint rule to make a change
  pass. Fix the cause, or stop and report the conflict.
- Do not remove or overwrite another contributor's work in progress.

### Commits and pull requests

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`,
  `chore:`. Scope with the layer where it helps: `feat(server): ...`.
- **Never add an AI agent as a commit co-author.**
- Never manually edit `CHANGELOG.md` or any file marked auto-generated.
- One logical change per commit. A contract change that touches both layers is
  one logical change and belongs in one commit.

---

## 5. Local development

Everything runs through Docker Compose from the repository root. The `Makefile`
is the entry point - prefer it over raw `docker-compose` invocations.

```bash
make dev
```

Starts both services with hot reload. Frontend on `http://localhost:3000`,
backend on `http://localhost:8000`, interactive API docs on
`http://localhost:8000/docs`.

| Command        | Purpose                                               |
| -------------- | ----------------------------------------------------- |
| `make dev`     | Start everything with hot reload (base + dev overlay) |
| `make build`   | Build both images (`TAG` defaults to `latest`)        |
| `make start`   | Start detached, production-shaped                     |
| `make stop`    | Stop services                                         |
| `make restart` | Stop then start                                       |
| `make logs`    | Follow logs for all services                          |
| `make status`  | Show service status                                   |
| `make cleanup` | Remove containers, networks, volumes, and images      |

Running a single layer natively - faster inner loop when you are only touching
one side - is documented in that layer's `AGENTS.md`.

### Before you claim a change works

Running the test suite is not the same as the feature working. For any
user-visible change, exercise it the way a user would: through the running app
at `http://localhost:3000`, or against the live API. For bug fixes, **reproduce
the bug end-to-end first** - a fix written without a reproduction usually fixes
something else.

Hold the UI to a high standard. If something looks visibly wrong while you are
in there - misalignment, wrong contrast, a number formatted inconsistently -
fix it or report it, even when it is not what you were asked to do. The same
applies to lint failures, flaky tests, and broken checks you pass through.

---

## 6. Packaging and deployment

Each layer builds an independent image from its own directory as build context:

| Service  | Context      | Image                     | Port |
| -------- | ------------ | ------------------------- | ---- |
| Backend  | `app/server` | `trading-backend:${TAG}`  | 8000 |
| Frontend | `app/client` | `trading-frontend:${TAG}` | 3000 |

- A Dockerfile may only reference files inside its own layer. Never reach up to
  the repository root or across to the sibling layer.
- Both Dockerfiles are multi-stage where it helps; the frontend `builder` stage
  is reused as the dev container.
- Target deployment is AWS - ECS/Fargate behind an API entry point, RDS
  PostgreSQL, ElastiCache Redis, ECR for images, Terraform for provisioning. See
  [docs/system-architecture.md](docs/system-architecture.md). Cloud
  infrastructure is not yet in this repository; when it lands it gets its own
  top-level directory and its own `AGENTS.md`.

---

## 7. Definition of done

A change is done when all of these are true:

1. The behaviour the story asked for works, verified the way a user would hit it.
2. Tests cover the new behaviour, including its failure and boundary cases.
3. The layer's own checks pass - see that layer's `AGENTS.md` for the commands.
4. No new lint errors, type errors, or warnings, including pre-existing ones in
   files you touched.
5. Documentation and the relevant `AGENTS.md` are updated if contributor-facing
   behaviour or structure changed.
6. Your handoff states plainly: what changed, what you verified and how, and what
   you could **not** verify. If a check could not run, say why. Never report a
   partial result as complete.

# Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project. Do not repeat what the codebase already shows; point to the authoritative file or command instead. Prefer rewriting or pruning existing entries over appending new ones. When updating this file, preserve this bar for all agents and keep entries concise. Use the skill `/docs-update` whenever new modules are created.
