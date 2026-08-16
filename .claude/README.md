# Claude Code adapter

This directory is a **Claude Code adapter**, not a source of truth.

All repository conventions - project structure, layering rules, coding
standards, verification commands, definition of done - live in the `AGENTS.md`
tree, starting at [/AGENTS.md](../AGENTS.md). That tree is tool-neutral so
collaborators using different agents work from the same instructions.

## What lives here

- `skills/` - Claude-specific task procedures (implementation, code review,
  debugging, docs updates). They describe *how to carry out a kind of task*.
  They must not restate repository conventions; they link to `AGENTS.md`
  instead.

## What must not live here

Conventions, repo maps, layering rules, or file-structure guidance. Those
duplicate `AGENTS.md`, and duplicated instructions drift apart until agents get
contradictory guidance.

A previous version of this directory contained `context/` and `workflows/`
folders whose every internal link pointed at a `.agents/` directory that never
existed, and which documented a server layout that had since changed. They have
been removed and their content folded into the `AGENTS.md` tree.

## Reading order for any task

1. [/AGENTS.md](../AGENTS.md) - always.
2. Each `AGENTS.md` on the path down to the directory you are editing.
3. The relevant skill under `skills/`.

The parent-child scope rules - including when cross-layer reading is allowed -
are defined in section 1 of the root file.
