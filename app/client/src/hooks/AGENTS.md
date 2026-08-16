# AGENTS.md - Hooks (`app/client/src/hooks`)

**Parent:** [app/client/AGENTS.md](../../AGENTS.md). Read it first for the
stack and the Server Component policy.

**Scope:** shared React hooks used by more than one component.

---

## When a hook belongs here

Only when **two or more** components already need it. A hook used in one place
belongs next to that component. Premature extraction into a shared folder makes
the dependency graph harder to read for no benefit.

## Rules

- Every file here is client-side: `'use client'` at the top.
- `useXxx` naming, one hook per file, filename matching the hook.
- Fully typed arguments and return value. Return an object for three or more
  values so call sites are not order-dependent.
- **No `fetch`.** Hooks call the typed client in `src/lib/api/`. A hook that
  builds a URL is doing the API layer's job.
- **No financial calculation.** Same rule as everywhere in this layer - the
  server computes, the client displays.
- Pure logic with no React dependency is not a hook. Put it in `src/lib/`.

## Async and effects

- Every request-driven hook exposes the full set of states the UI needs:
  loading, error, data, and empty. A hook that returns only `data` forces every
  caller to reinvent the other three inconsistently.
- Clean up in the effect's return: abort in-flight requests, clear timers, close
  sockets. An unaborted request that resolves after unmount sets state on a dead
  component and, on a portfolio screen, can flash the previous user's data.
- Declare complete dependency arrays. Do not silence the exhaustive-deps lint
  rule - if it complains, the effect is usually doing too much.
- Never call a hook conditionally or inside a loop.

## Prefer the framework first

Before writing a data-fetching hook, check whether the route can fetch on the
server instead. Server Components with `async` data loading remove the loading
state entirely, and that is almost always the better UI.

Client-side fetching is for data that genuinely changes after render: live
prices, user interactions, polling.

## Testing

Test hooks through `renderHook`, asserting the state transitions - initial,
loading, resolved, error - and that cleanup actually runs on unmount. Stub the
API client, never the global `fetch`.
