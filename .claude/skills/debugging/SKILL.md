---
name: debugging
description: Use when diagnosing failing commands, broken runtime behavior, CI failures, or unexpected results.
---

# Skill: Debugging

Use this skill when diagnosing failing commands, broken runtime behavior, or unexpected results.

## Process

- Start from the exact error, symptom, or failing command.
- Reproduce the failure when feasible.
- Inspect the narrowest relevant path before editing.
- Change one cause at a time.
- Re-run the most relevant check after the fix.

## Common Areas

- Client runtime or build issues: inspect `app/client/package.json`, `app/client/src/`, and `app/client/next.config.mjs`.
- Server runtime issues: inspect `app/server/app/main.py`, then follow the request
  down the layers - `app/server/app/api/`, `app/server/app/service/`,
  `app/server/app/domain/`, `app/server/app/data/`. The layer map is in
  `app/server/AGENTS.md`.
- Wrong numbers rather than errors: start in `app/server/app/domain/` and
  `app/server/app/service/`, where positions and PnL are derived. Reproduce with
  a failing test before changing anything.
- Docker issues: inspect `app/client/Dockerfile`, `app/server/Dockerfile`, and compose configuration.

## Handoff

State the root cause, the fix, and the verification result.
