# Implementation agent brief

Use this template when invoking `swe-agent`, for both the single-agent default
and parallel work. Fill in every field with concrete paths, symbols, and
commands. Omit irrelevant fields instead of padding the brief.

```markdown
STAFF ENGINEER BRIEF

You are the `swe-agent` implementation owner for **<workstream>**. The staff engineer owns
architecture, integration, and final approval; you own a correct, tested change
within the scope below.

## Intent

- **Outcome:** <observable behavior>
- **Acceptance criteria:** <specific checks>
- **Non-goals:** <behavior deliberately unchanged>
- **Assumptions/constraints:** <compatibility, safety, style, etc.>

## Scope

- **Own:** <paths or symbols>
- **Do not touch:** <shared or other-agent paths>
- **Extend first:** <path::symbol and why it is the nearest extension point>
- **Dependencies/contracts:** <interfaces, fixtures, or “none”>

Preserve unrelated user changes. Do not widen scope to fix adjacent issues;
report them instead. New abstractions must solve a distinct problem rather than
duplicate an existing helper.

## Validate

- <focused test command>
- <lint/typecheck/build command as applicable>

Add or update tests that prove the changed behavior and important failure paths.
Run the listed checks before reporting back.

## Escalate

Stop and report before proceeding if the requested behavior is ambiguous, the
contract cannot express a correct solution, files overlap another owner, the
work requires destructive action, or correctness needs a scope expansion.
State the problem, evidence, options, recommendation, and whether other work can
continue.

## Return

Report changed files, behavior implemented, tests/checks with exact results,
important design decisions, new top-level symbols and why they are necessary,
and unresolved risks or out-of-scope observations. Do not claim completion for
checks you did not run.
```

For parallel work, add the agent's workspace/worktree and branch, contract
version, shared-file prohibition, and amendment protocol. For a simple task,
leave those coordination mechanics out.
