# AGENTS.md - Data layer (`app/server/app/data`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule and backend conventions.

**Scope:** repository implementations and every persistence detail. Also the
home for outbound provider adapters.

---

## Position in the architecture

This layer **depends inward on the domain** and satisfies interfaces it does not
own. `app/domain/repositories.py` declares the protocol; the classes here
implement it. The domain never imports this directory.

That inversion is what lets the in-memory store be swapped for PostgreSQL
without touching a service, a route, or a business rule.

## Imports

- **May import:** `app/domain/` (entities and protocols), and persistence or
  client libraries.
- **Must not import:** `app/api/`, `app/api_contracts/`, or `app/service/`.

## Rules

- **Implement the protocol exactly.** Do not add public methods a service needs
  but the protocol does not declare - add them to the protocol first, or the
  abstraction has a hole in it.
- **Return domain entities**, never storage records, rows, or ORM objects.
  Translation happens here and stops here.
- **Never leak the backing store upward.** No SQL, no session, no
  `sqlalchemy.exc` exception escaping into a service.
- **Never enforce a business rule here.** A repository stores and retrieves. It
  does not decide whether a sell is valid.
- Every method is `async`, including in-memory ones, so the interface does not
  change shape when a real driver arrives.

## Ownership scoping

Every read and write is scoped by `owner_id`. The signatures are
`get_by_owner(owner_id, entity_id)`, not `get(entity_id)`, deliberately: a
lookup that can return another user's holding is a data breach waiting for a
bug. Preserve that shape when adding methods, and never add an unscoped
accessor.

## Current implementation

In-memory dictionaries keyed by `(owner_id, entity_id)`. They are real
implementations, not test doubles - the service test suite runs against them.

Store copies rather than shared references where mutation could leak between
the caller and the store.

## Naming

- `<backing>_<context>_repositories.py`, e.g. `in_memory_portfolio_repositories.py`,
  later `sql_portfolio_repositories.py`.
- ORM/table models go in `data/models.py` when persistence lands - **never** in
  `app/domain/` or `app/api_contracts/`. Domain entities and table rows are
  separate types that happen to look similar today.

## Provider adapters

Outbound integrations - market data, LLM providers, object storage - are also
data-layer concerns. Each gets an interface owned by this codebase and an
implementation here, per the provider rule in the root file. A service calls
`MarketDataProvider`, never `yfinance` or a vendor SDK directly.

Sync-only client libraries are isolated here and run in a thread executor so
they cannot block the event loop.

## Testing

A new repository implementation must pass the **same test suite** as the
existing one. Write the protocol tests once and parametrize over
implementations, so PostgreSQL is proven equivalent to in-memory rather than
assumed to be.
