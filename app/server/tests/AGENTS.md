# AGENTS.md - Backend tests (`app/server/tests`)

**Parent:** [app/server/AGENTS.md](../AGENTS.md). Read it first for the layering
rule and the verification commands.

**Scope:** how backend tests are written and where each kind belongs.

---

## Where a test goes

Test each behaviour at the layer that owns it. Testing the same rule at three
levels produces a suite that is slow to run and painful to change.

| What you changed | Where the test goes | Style |
|---|---|---|
| A business rule or calculation | Domain test | Construct entity, call method, assert. No mocks, no I/O. |
| Coordination across entities or repositories | Service test | Real in-memory repositories, not mocks. |
| A route, status code, or DTO | API test | `httpx` against the app; assert status and shape only. |
| A repository implementation | Repository test | Shared protocol suite, parametrized over implementations. |

Push tests down. If a bug is reachable in the domain, test it in the domain -
that test is faster, clearer, and survives refactors of the layers above it.

## Financial calculations

Every test of a money calculation asserts a **hand-computed expected value**.

Never assert against whatever the implementation currently returns, and never
recompute the expected value using the same formula the code uses. Both patterns
produce a test that passes while the number is wrong, which is the exact failure
this suite exists to prevent.

Required cases for any position or PnL change:

- zero quantity, and the transition to zero on a full exit
- partial sell, and a sequence of buys at different prices
- fees included in cost basis
- a sell that would go negative - assert the error **and** that state is
  unchanged afterwards
- out-of-order trade dates, since position is replayed in trade-date order

## Conventions

- `pytest`, files as `test_<module>.py`, functions as
  `test_<behaviour>_<condition>`. The name states the expectation:
  `test_sell_exceeding_quantity_raises_oversell_error`.
- Async tests need `pytest.mark.asyncio` (or `anyio`); the service and
  repository layers are async throughout.
- One behaviour per test. A test that asserts five unrelated things reports one
  failure and hides four.
- Fixtures build valid domain objects. Keep test data obvious - `100` units at
  `10.00` reads better than realistic-looking noise.
- No network, no clock dependence, no ordering dependence between tests. Inject
  time rather than asserting against `utcnow()`.

## Mocks

Prefer real in-memory implementations. Mock only at a genuine external boundary
- a market data provider, an LLM provider - and mock the **interface this
codebase owns**, never a vendor SDK.

A test that asserts a mock was called with certain arguments is testing the code
against itself. Assert on resulting state instead.

## Coverage

Proportional to risk, not to a percentage target. Financial calculations and
domain rules approach complete coverage. Wiring and glue do not need a test for
their own sake.

Every bug fix ships with a test that fails before the fix and passes after. If
you cannot write that test, you have not found the bug yet.
