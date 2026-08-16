# AGENTS.md - Presentation: routers (`app/server/app/api`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule, API design conventions, and error handling policy.

**Scope:** FastAPI routers. The HTTP boundary and nothing else.

---

## What a route does

Exactly four things:

1. Accept a validated request DTO from `app/api_contracts/`.
2. Call one service method.
3. Map domain errors to HTTP status codes.
4. Return a response DTO.

If a route is doing anything else - a calculation, a loop over repositories, a
conditional about what is financially valid - that work belongs in
`app/service/` or `app/domain/`.

A route body should read as a single call surrounded by translation.

## Imports

- **May import:** `app/service/`, `app/api_contracts/`, `app/dependencies.py`,
  and domain error types from `app/domain/models.py`.
- **Must not import:** anything from `app/data/`. A route never sees a concrete
  repository.

Services arrive via `Depends(get_...)` from `app/dependencies.py`. Never
instantiate a service inside a route.

## Error mapping

This is the **only** place a domain error becomes an HTTP status. The mapping is
a deliberate product decision, so keep it explicit and consistent:

| Domain outcome | Status |
|---|---|
| Service returns `None` for a lookup | `404` |
| `HoldingNotFoundError` on a nested write | `404` |
| `OversellError` | `409` |
| `HoldingHasTransactionsError` | `409` |
| DTO validation failure | `422` (FastAPI handles this) |

Never let a domain exception escape as an unhandled `500`. If you add a domain
error, add its mapping here in the same change.

Error details are safe to show a user: state the rule that was broken, never
leak internal identifiers, stack traces, or other users' data.

## Router setup

- One module per bounded context, exporting `router`.
- Prefix and tags on the `APIRouter`, not repeated per route:
  `APIRouter(prefix="/users/{user_id}/portfolio", tags=["portfolio"])`.
- Register in `app/main.py`. Registration is the only thing `main.py` does with
  routes.
- Declare `response_model` and an explicit `status_code` on every route - they
  are the OpenAPI schema the frontend generates its types from.

## Ownership of the contract

The frontend reads this layer's schema to build its client. A rename or removal
here is a breaking change for a separate deployable. Additive changes are safe;
breaking ones must be coordinated with `app/client` in one commit.

## Testing

Route tests use `httpx` against the app and assert **status codes and response
shapes**. Business behaviour is already covered at the service and domain level
- do not re-test it through HTTP. What only these tests can catch is a wrong
status code or a DTO that does not serialize.
