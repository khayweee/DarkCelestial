# AGENTS.md - Domain layer (`app/server/app/domain`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule and backend conventions.

**Scope:** business entities, business rules, domain errors, and repository
protocols. The centre of the architecture.

---

## The one rule

**This directory imports nothing from outside itself except the standard
library.**

No FastAPI. No Pydantic. No SQLAlchemy. No HTTP clients. No LangChain. Nothing
from `app/api/`, `app/api_contracts/`, `app/service/`, `app/data/`, or
`app/agents/`.

If you need something from an outer layer here, the design is wrong. The
dependency is pointing the wrong way and the logic belongs somewhere else.

You should be able to delete every other directory in this service and the
domain would still import, still be testable, and still be correct.

## Files

| File | Contents |
|---|---|
| `models.py` | Entities (`PortfolioHolding`, `PortfolioTransaction`), value types (`TransactionSide`), domain errors, normalization helpers |
| `repositories.py` | `typing.Protocol` interfaces the data layer must satisfy |

## Entities

- `@dataclass`, never Pydantic. Pydantic is a serialization concern and belongs
  to `app/api_contracts/`.
- Construct through a `create()` classmethod so invariants and identity are
  established in one place. Do not build an entity field-by-field from outside.
- Normalize on the way in: symbols, exchanges, and currencies are uppercased and
  stripped. A holding in `aapl` and one in `AAPL` are the same holding.
- An entity may mutate itself through its own methods. Callers do not reach in
  and assign fields.

## Business rules that live here

These are true regardless of transport or storage, so they are enforced here and
not re-checked in the route:

- A sell cannot exceed the current holding quantity.
- A holding with transaction history cannot be silently deleted.
- Position quantity and average cost are **derived by replaying the transaction
  history** over the initial position, in trade-date order. They are never set
  directly by an outer layer.
- Buy transactions fold fees into cost basis. Selling to zero resets average
  cost.

## Errors

All inherit `PortfolioError`. They describe a business failure and carry **no
HTTP status code and no HTTP language** - `app/api/` decides what a violation
means over HTTP. Name them for the rule that was broken (`OversellError`), not
for the response (`BadRequestError`).

## Adding a new bounded context

Phase 2 and 3 bring performance analytics, benchmarks, and risk exposure. When a
new context is substantial, give it its own module (`domain/performance.py`)
rather than growing `models.py` indefinitely. Keep contexts from importing each
other's internals.

## Numeric precision

Per the root file, monetary values must not be binary floats. The current
entities use `float`; that is known debt scheduled for migration to `Decimal`.
**Do not add new float-based money fields.** When you touch a calculation here,
prefer moving it toward `Decimal` over extending the float path.

## Testing

Domain logic is the cheapest thing in the repository to test and the most
expensive to get wrong. Every rule above gets a direct unit test with no mocks,
no fixtures, and no I/O - construct the entity, call the method, assert the
number.
