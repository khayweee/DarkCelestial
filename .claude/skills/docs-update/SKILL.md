---
name: docs-update
description: Use when adding or changing contributor-facing documentation, agent instructions, workflow guidance, or framework adapters.
---

# Skill: Documentation Update

Use this skill when adding or changing contributor-facing documentation, agent instructions, or workflow guidance.

## Process

- Canonical agent guidance lives in the `AGENTS.md` tree, starting at `/AGENTS.md`.
- `CLAUDE.md` files and everything under `.claude/` are adapters and hold no
  conventions of their own.
- Put a rule in the directory it governs. Never restate a parent rule in a child
  `AGENTS.md`; a child may narrow a parent rule, never contradict it.
- Prefer links to canonical files over duplicated instructions.
- Update the tree diagram in `/AGENTS.md` when adding or removing an `AGENTS.md`.
- Update the affected `AGENTS.md` in the same change as the structural or
  workflow change it describes.

## Handoff

Summarize which docs changed and how future agents should use them.
