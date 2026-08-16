# Contract template

The contract lives at `contracts/<feature>/CONTRACT.md` next to the stubs it
describes, written for an agent who can see one side of a seam and can't ask
the other side a question.

Every field below exists to prevent a specific integration failure. If a
section doesn't apply, write "n/a" and why, rather than deleting it.

---

## Header

```markdown
# Contract: <feature>

**Version:** 1
**Base commit:** <sha>
**Layers:** <layer-a>, <layer-b>, <layer-c>
```

Agents quote the version when reporting progress or raising an amendment, so a
stale branch is visible immediately.

## Layers

One entry per layer. State ownership as paths - "the API layer" is ambiguous,
`src/api/**` is not.

```markdown
### <layer-name>

- **Delivers:** one sentence on the behavior this layer is responsible for
- **Owns:** src/path/**, tests/path/**
- **Must not touch:** contracts/**, src/other-layer/**
- **Depends on:** which seams it consumes, which it provides
- **Extend, do not recreate:** `src/existing/module.ts::existingFunction` handles
  the nearest existing behavior; grow it rather than adding a parallel one
- **Done when:** its tests pass against the fixtures with other layers still stubbed
```

The "extend, do not recreate" line is the payoff of the survey - it prevents a
duplicate helper that would otherwise surface (or not) at review.

## Seams

One entry per boundary between two layers - the part agents read most.

```markdown
### Seam: <layer-a> -> <layer-b>

**Interface:** `src/domain/ports.ts::OrderRepository` (stub committed at base)

**Operations**

| Operation  | Input     | Returns         | Preconditions   | Errors                      |
| ---------- | --------- | --------------- | --------------- | --------------------------- |
| `findById` | `OrderId` | `Order \| null` | id is non-empty | throws `StorageUnavailable` |

**Semantics.** What each operation means beyond its signature: ordering
guarantees, idempotency, read consistency, what "null" means versus an error,
partial-failure behavior.

**Invariants.** What's always true of data crossing this seam - e.g. money as
integer minor units, timestamps as UTC ISO-8601, collections never null (only
empty).

**Ownership of validation.** Which side validates, which may assume valid
input, which normalizes. Both sides assuming the other checked is the most
common correctness hole in parallel work.

**Out of scope.** What the consumer must not expect this seam to do.
```

The errors column matters most: agents agree on happy paths by default and
diverge on failure paths by default, and that's where integration bugs live.

## Fixtures

```markdown
## Fixtures

Shared examples both sides assert against, at `contracts/<feature>/fixtures/`.

- order.valid - the canonical happy path
- order.minimal - only required fields present
- order.edge-null-discount - the nullable field actually null
```

Fixtures catch what types can't: whether a field is really optional, what an
empty collection looks like, how a decimal is encoded. Both sides testing
against the same bytes fails in a layer's own test run instead of at
integration.

## Amendment log

Append-only - never rewrite history; a rejected request is as informative as
an accepted one, and the log is the merge-time propagation checklist.

```markdown
## Amendments

### A1 (v1 -> v2) - raised by <layer>, accepted

**Problem:** `findById` cannot express a record whose payment leg failed to load,
so the transport layer would have to guess between "missing" and "broken".
**Change:** returns `Order | PartialOrder | null`; `PartialOrder` added to ports.
**Affects:** persistence, domain, transport
**Propagated:** persistence (yes), domain (yes), transport (yes)

### A2 - raised by <layer>, rejected

**Request:** expose the raw database row on the port.
**Reasoning:** that pushes storage detail across the seam, which is the coupling
this layer split exists to prevent. Use `toDomain()` at the boundary instead.
```

The `Propagated` line is the one that gets forgotten - forgetting it is how a
run ends up with branches built against different contract versions.
