# AGENTS.md - Presentation: DTOs (`app/server/app/api_contracts`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule and API design conventions.

**Scope:** Pydantic request and response models. The wire format.

---

## What these are

The public shape of the API. They are a **translation layer**, deliberately kept
separate from domain entities so that the wire format and the business model can
evolve independently.

Never expose a domain entity directly from a route. The moment you do, every
internal field rename becomes a breaking API change.

## Imports

- **May import:** Pydantic, stdlib, and domain enums where the wire value is
  genuinely the same term (for example `TransactionSide`).
- **Must not import:** `app/service/`, `app/data/`, repository protocols, or
  domain entities for use as a base class.

## Conventions

- Suffix by direction: `HoldingCreateRequest`, `HoldingResponse`,
  `HoldingUpdateRequest`.
- Responses are built with `Model.model_validate(entity)` and need
  `model_config = ConfigDict(from_attributes=True)`.
- Update requests use `| None = None` for every field so a partial update means
  "leave unspecified fields alone". Do not reuse a create model for updates -
  they have different required-field semantics.
- `user_id` comes from the path, never from the request body. A body-supplied
  owner is an authorization hole.

## Validation belongs here

Pydantic enforces **structural and input-range** constraints so bad input is
rejected at the boundary with a `422` before any service runs:

- Quantities and prices are positive.
- Fees are non-negative.
- Currency is a 3-letter code; symbols and exchanges are non-empty.
- Trade dates are dates, not datetimes.

Use `Field(gt=0)`, `Field(ge=0)`, and `min_length` rather than hand-written
checks.

**Do not put business rules here.** "Quantity must be positive" is input
validation and belongs here. "You cannot sell more than you hold" depends on
portfolio state and belongs in `app/domain/`. The test: if the rule needs to
look at stored data, it is not validation.

## Money on the wire

Serialize monetary values as strings, not JSON numbers, once the `Decimal`
migration lands - JSON numbers are IEEE 754 doubles in most parsers and will
silently round a user's cost basis. Currency travels with every amount; a bare
number in a multi-currency portfolio is ambiguous.

## Changing a contract

Adding an optional field is backward compatible. Renaming a field, removing one,
making an optional field required, or changing its type is **breaking** for the
frontend deployable - coordinate it and change both sides in one commit.
