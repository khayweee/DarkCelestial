# Staff engineer review checklist

Review in this order. Stop and fix correctness or contract failures before
spending time on polish. Record actionable findings with file and line.

## Intent and scope

- The observable behavior matches every acceptance criterion.
- Assumptions remain valid and non-goals remain unchanged.
- The diff contains no unrelated cleanup or overwritten user work.
- Every changed file had one clear owner; parallel work did not diverge on a
  shared interface, fixture, or convention.

## Correctness

- Read the complete diff and relevant callers, not only the agent report.
- Tests exercise the changed behavior and important failure/edge paths.
- Cross-layer changes have a real integration or end-to-end check; mocks do not
  merely agree with one another.
- Errors are handled where actionable; validation and normalization happen on
  the documented side of each boundary.
- Units, time zones, encodings, nullability, ordering, idempotency, and partial
  failures retain their intended meaning.
- Concurrency, migrations, compatibility, and rollback are addressed when in
  scope.

## Architecture and maintainability

- The change extends the nearest existing behavior where appropriate.
- New modules and top-level symbols represent distinct abstractions rather than
  convenience duplicates.
- Dependency direction and layer boundaries remain intact; framework, storage,
  and transport details do not leak across seams.
- Parallel agents did not create near-identical helpers, double validation, or
  divergent error/logging/test conventions.
- Names use repository vocabulary; code has no dead paths, debug output,
  commented-out blocks, secrets, or environment-specific paths.
- Complexity is proportionate; comments explain non-obvious reasons, not syntax.

## Verification

- Focused tests pass.
- Relevant lint, format, typecheck, and build checks pass.
- The broader suite passes in proportion to the blast radius.
- Any check not run is named with the reason and resulting risk.
- The final diff is re-read after fixes; resolved findings are retested.

## Disposition

Return layer-local findings to the original owner while its context is warm.
Coordinate seam-level corrections centrally. Approve only when the intent is
met, material findings are resolved, and the evidence supports completion.
