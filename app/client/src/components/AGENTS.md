# AGENTS.md - Components (`app/client/src/components`)

**Parent:** [app/client/AGENTS.md](../../AGENTS.md). Read it first for the
stack, the Server Component policy, the composition and dependency-direction
rule, and the money-formatting and accessibility rules.

**Scope:** reusable UI and feature components.

---

## The two folders

```
components/
├── ui/         Generic, product-agnostic primitives
└── features/   Portfolio-aware components
```

| | `ui/` | `features/` |
|---|---|---|
| Knows about | Nothing but its props | Portfolio domain types |
| May import | Other `ui/`, `lib/format` | `ui/`, `hooks/`, `lib/` |
| Must not | Import from `features/` or `lib/api` | Call `fetch` directly |
| Example | `Heading`, `Text`, `Button`, `Table`, `Badge`, `Skeleton` | `HoldingsTable`, `PnLBadge`, `AllocationChart` |

`ui/` never imports `features/`. That dependency only points one way, and a
`ui/` component that mentions a holding or a transaction is in the wrong folder.

### `ui/` is where visual consistency is enforced

`ui/` is the bottom of the dependency graph, so everything may import it freely -
any feature, any route, any nesting depth. That is the point of the folder.

Text and layout primitives in particular are **used, not re-implemented**:
headings and titles, body and secondary text, labels, section headers, cards,
spacing wrappers. A raw `<h2>` or `<p>` styled inline inside a feature is a
private copy of the type scale that will drift from every other copy, and drift
in typography is what makes a product look assembled by different people.

This is not a ban on semantic tags - it is the opposite. A `Heading` renders a
real `<h1>`-`<h6>` chosen by its level prop, and `Text` renders a `<p>`. The
primitive is what guarantees the tag and the visual weight stay in step, so a
designer's request to make something look smaller cannot quietly demote a
heading level in the document outline.

When a primitive does not exist yet, add it here. When it nearly fits, change it
here and let every caller benefit. Neither of those is a reason to style locally.

## Rules

- **Presentational by default.** Components receive data through props. They do
  not fetch. Data enters at the route (see [src/app/AGENTS.md](../app/AGENTS.md))
  and flows down.
- **No `'use client'` unless the component itself needs browser state, effects,
  or event handlers.** Put it on the interactive leaf, not the container that
  renders it.
- **No financial calculation.** A component that sums, divides, or annualises is
  duplicating the server and will eventually disagree with it. Display what the
  API returned.
- **Format through `src/lib/format/`.** No `toFixed()`, no manual currency
  symbols, no locale string assembly inline.
- One component per file, named export matching the filename in `PascalCase`.
- Props typed with an explicit interface. No `any`, no implicit `any` on a
  handler.

## Financial display components

The components that render money carry most of this app's credibility, so they
get specific requirements:

- Numeric columns are **right-aligned with tabular figures**
  (`font-variant-numeric: tabular-nums`), so digits line up down the column.
- Gains and losses need a **sign or a label**, not colour alone. Colour-only
  encoding is invisible to colour-blind users and disappears in print.
- Always render the currency alongside the amount.
- Holdings tables are real `<table>` elements with `<th scope>` headers. A
  `<div>` grid is unreadable to a screen reader.
- Every component renders sensibly with zero, one, and many rows, and with a
  negative value.

## Decomposition

The parent file owns the rule: decide what a component is made of before writing
it, split on responsibility, and never import a sibling. Three narrowings apply
here.

**A `features/` component is assembled from `ui/` primitives.** If it is writing
raw markup for something visual that carries no domain meaning - a badge, a
skeleton row, an empty state, a disclosure - that markup is a `ui/` primitive it
should be importing instead. Domain knowledge is the only thing `features/` adds.

**A feature folder is one parent plus the children only it uses.**

```
features/
└── holdings/
    ├── HoldingsTable.tsx       the parent this folder exists for
    ├── HoldingsRow.tsx         used only by HoldingsTable
    └── HoldingsEmptyState.tsx  used only by HoldingsTable
```

The moment a second feature folder needs one of those children, it stops being
private: move it up to `features/` if it is domain-aware, down to `ui/` if it is
not. **Do not reach into another feature folder.** `transactions/` importing
`holdings/HoldingsRow.tsx` couples two features through a file written for one of
them, and neither can be changed safely afterwards.

This bans reaching into a neighbour's private children, not sharing. Two feature
folders importing the same `ui/` primitive - the same `Heading`, the same
`Table`, the same `PnLBadge` at the `features/` root - is the intended path and
needs no justification.

**Decompose early, generalise late.** These pull in opposite directions and both
are real. Splitting a parent into named children is free and always worth doing.
Making a child *reusable* - adding props for cases nobody has asked for, widening
a type to fit a hypothetical second caller - is not. Duplicate once, extract on
the third. A component with eight boolean props is the failure mode: it wants to
be three components.

## Testing

Test behaviour a user can observe, using Testing Library queries by role and
accessible name - not by class name or test id, which do not tell you the
component is usable.

Worth testing: a `ui/` primitive's variants and disabled/loading states; a
`features/` component's rendering of negative values, zero, empty, and long
values that could overflow. Not worth testing: that a static label renders.
