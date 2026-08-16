# AGENTS.md - Application layer (`app/server/app/service`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule and backend conventions.

**Scope:** use cases. One service method per thing a user can do.

---

## What belongs here

Coordination. A service method orchestrates domain entities and repository
protocols to complete a single use case, and owns the consistency of the result.

It does **not** own the business rules themselves - those live in
`app/domain/`. If a method is growing conditional logic about what is
financially valid, that logic is in the wrong place.

## Imports

- **May import:** `app/domain/` (entities, errors, repository protocols).
- **Must not import:** FastAPI, `app/api/`, `app/api_contracts/`, or any
  concrete class from `app/data/`.

Repositories arrive through the constructor, typed as the domain `Protocol`.
A service never constructs its own repository and never knows whether it is
talking to memory or PostgreSQL.

## Signatures

- Accept and return **domain objects and primitives**. Never a Pydantic request
  or response model - that would couple the use case to HTTP.
- `async` throughout.
- Return `None` for "the thing does not exist". Raise a domain error for "the
  rule was violated". The route maps each to a status code.

## Consistency

This layer keeps derived state correct. When a transaction is created, updated,
or deleted, the affected holding is recomputed from its full transaction history
in the same call - the caller never has to remember to do it.

**Failed writes must not leave partial state.** The existing pattern is
compensating action: write, attempt the recompute, and on a domain error undo
the write and re-raise. See `create_transaction` and `update_transaction` in
`portfolio_service.py`.

That pattern is a stand-in for a real transaction boundary. When PostgreSQL
lands, this layer owns the unit of work and the compensating logic goes away -
do not build more of it in the meantime than you need.

## Naming

`<context>_service.py`, class `<Context>Service`. Methods read as the user
action: `create_holding`, `list_transactions`, `delete_holding`. Private helpers
are `_`-prefixed.

## Testing

Services are tested against **real in-memory repositories**, not mocks. The
in-memory implementations in `app/data/` exist partly for this - they make the
tests exercise real coordination instead of asserting that a mock was called.

Cover the compensating paths explicitly: a sell that oversells must leave both
the transaction store and the holding exactly as they were.
