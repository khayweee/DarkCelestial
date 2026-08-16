# AGENTS.md - Frontend (`app/client`)

**Parent:** [/AGENTS.md](../../AGENTS.md). Read it first. Universal rules -
money handling, UTC, secrets, dependencies, commits, definition of done - live
there and are not repeated here.

**Scope of this file:** the Next.js application. Stack, structure, data access,
state, styling, testing, and the commands that verify a frontend change.

**Do not read `app/server/**` while implementing a frontend story.** The
exception is confirming an API contract, which is covered in section 5.

---

## 1. Stack

- **Next.js 16, App Router.** Not the Pages Router - section 3 says where pages
  actually live.
- **React 19**, Server Components by default.
- **TypeScript 7, strict mode.** See section 2 - this is a migration in progress.
- **Vitest 4 + React Testing Library** for unit and component tests.
- **ESLint + Prettier**, `next/core-web-vitals` as the base config.

Desktop-first, but responsive from the start. A mobile app is a future path
sharing this API contract, so keep layout logic out of business logic.

### Staying current

Every dependency starts at its current stable major. Before adding or upgrading
one, check what that is - do not copy a version out of an older file, another
project, or memory:

```bash
npm view <package> version
```

- **Pin exact versions** in `package.json`. A caret range lets two contributors
  and CI resolve different trees from the same commit, which turns a dependency
  bug into an unreproducible one.
- **A major upgrade is its own commit.** Never fold one into a feature change.
  It ships green on `npm run lint && npm run test && npm run build` and loaded in
  a browser, because build success does not prove a runtime behaviour survived.
- The versions above are the floor at the time of writing, not a ceiling. If the
  registry has moved past them, take the newer one and update this file in the
  same commit.

---

## 2. Current state vs required state

**Read this before assuming a command exists.**

The directory currently contains a placeholder WebSocket "Trading Assistant"
dashboard left over from an earlier product direction. It is **not** the
portfolio tracker and carries no conventions worth preserving.

| | Current | Required |
|---|---|---|
| Framework | Next 14.2, React 18 | Current stable majors, per section 1 |
| Language | `.jsx`, no types | TypeScript strict, `.tsx` |
| Lint | none | ESLint + Prettier, `npm run lint` |
| Tests | none | Vitest, `npm run test` |
| UI | Placeholder WS dashboard | Portfolio tracker |
| API access | Raw `WebSocket` in a page component | Typed client in `src/lib/api/` |
| Config | Inline literals in the page | `src/lib/config.ts`, per section 4 |

Until the bootstrap below is done, **do not invent commands**. If you are asked
to verify and the script does not exist, say so rather than reporting a check
you did not run.

Bootstrap, in order, when a story first requires it:

1. Upgrade Next and React to the current majors. This is not a version bump:
   from Next 15 onward `params`, `searchParams`, `cookies()`, and `headers()`
   are async, so anything reading them must be awaited. Do it in its own commit.
2. Add TypeScript, `tsconfig.json` with `"strict": true`, and `@types/*`.
3. Add ESLint (`eslint-config-next`) and Prettier, wire `lint` and `format`
   scripts.
4. Add Vitest, `@testing-library/react`, `jsdom`, and a `test` script.
5. Convert `layout.jsx` and `page.jsx` to `.tsx` and delete the placeholder
   dashboard when the first real page replaces it.
6. Rename the package from `trading-assistant-client` - it names a product this
   repository is no longer building.

Write new files as `.tsx` from day one, even before the conversion runs.

---

## 3. Structure

```
app/client/
├── src/
│   ├── app/            Route segments - one folder per page  -> src/app/AGENTS.md
│   ├── components/     Reusable UI + feature components      -> src/components/AGENTS.md
│   ├── hooks/          Shared client hooks                   -> src/hooks/AGENTS.md
│   └── lib/            API client, formatting, config, types -> src/lib/AGENTS.md
├── public/             Static assets served as-is
├── next.config.mjs
├── package.json
└── Dockerfile
```

Nothing outside `src/` is application source. Anything two routes both need
moves down into `components/`, `hooks/`, or `lib/` rather than being imported
sideways - the dependency rule is in section 4.

### Where pages live

This app is a single-page application: one document load, then client-side
navigation. In the App Router the equivalent of a `pages/` directory **is
`src/app/` itself** - every `src/app/<segment>/page.tsx` is one page of the
product, and the router handles the transitions between them. To see the list of
pages, read `src/app/`. There is no second place to look.

**Do not create a `pages/` directory.** Next.js reserves that name for the legacy
Pages Router. Adding one puts two routers in the same project competing for the
same URLs, and the resulting behaviour depends on resolution order rather than on
anything a reader can see.

Navigate with `next/link` and `useRouter` from `next/navigation`. A plain
`<a href>` to an internal route triggers a full document reload, throwing away
the client cache and the scroll position - the exact thing this architecture
exists to avoid. External links are still `<a>`.

### Keeping the directory clean

Frontend artifacts accumulate silently, and a directory nobody trusts is a
directory nobody reads.

- **`src/` is application source and nothing else.** Build output, scratch
  scripts, downloaded fixtures, and screenshots do not live there.
- **Static assets go in `public/`**, referenced by root-relative path
  (`/logo.svg`). No binaries committed under `src/`.
- **Generated output is never committed** - `.next/`, `node_modules/`,
  `coverage/`, `*.tsbuildinfo`. If you find any of it tracked, remove it and
  extend `.gitignore` in the same change.
- **There is exactly one frontend, at `app/client`.** A second copy of the app
  elsewhere in the repository is dead weight, not a backup. Delete it rather
  than keeping two trees in sync.
- **Delete on the way out.** A component, hook, route, asset, or config entry
  whose last reference disappears is removed in the change that orphans it.
  Unreferenced files are read as intentional by the next agent.

---

## 4. Rules that apply across the whole frontend

### Server Components by default

Add `'use client'` only when the file genuinely needs browser state, effects,
event handlers, or browser APIs. Push it to the **leaf** component, never the
page or layout. A `'use client'` at the top of a route tree opts the entire
subtree out of server rendering.

### Composition and dependency direction

Every screen is built by composition: a page is assembled from feature
components, a feature component from primitives. React has no component
inheritance - a parent is defined entirely by the children it composes, so
"what is this made of" is the only structural question worth asking.

**Decide what a component is made of before you write it.** A component that
renders more than one distinct thing - a header and a table, a summary and a
chart, a form and the result of submitting it - is a parent whose children have
not been named yet. Name them, and let the parent do nothing but arrange them.
Do this at design time: splitting a 400-line component afterwards touches every
import and every test, while starting with three files costs nothing.

Split on **responsibility, not line count**. If you cannot state a child's job
in one sentence without the word "and", it is not a child yet - and a piece
extracted purely to make a file shorter is indirection, not structure.

**Dependencies point down, never sideways.** A component may import its
children. It may not import its siblings.

When two components at the same level need the same thing, that thing is not a
sibling - it is a shared child. Move it down into `components/ui/`, `hooks/`, or
`lib/`, where both parents reach it by pointing downward. A sideways import is
always the symptom that something sits at the wrong level; it is never the fix.

**Shared primitives sit below everything and are imported from everywhere.**
`components/ui/` - headings, body text, labels, buttons, cards, badges, tables,
skeletons - is the bottom of the graph. Any page, any feature, any depth may
import from it, and doing so is a downward import, not a sideways one. This is
not an exception to the rule; it is what the rule is for.

Use those primitives rather than re-declaring the same thing locally. A feature
that writes its own `<h2>` with its own margin and weight has not avoided a
dependency, it has forked the type scale - and the fifth one to do it is how a
product ends up with five heading sizes. If a primitive is missing, add it to
`ui/`; if it does not fit, fix the primitive.

Each directory narrows this rule to its own edge: routes must not import each
other ([src/app/AGENTS.md](src/app/AGENTS.md)), and `ui/` must not import
`features/` ([src/components/AGENTS.md](src/components/AGENTS.md)).

### No business logic in the client

Cost basis, realized and unrealized PnL, CAGR, allocation weights, and benchmark
comparison are **computed by the server**. The client displays what the API
returns.

The client must never recompute a number the API already provides. Two
implementations of one financial formula will disagree, and the user will see
two different answers for the same portfolio.

The client may format - currency symbols, decimal places, percent signs, locale
grouping, red/green sign colouring - and nothing more.

### Rendering money and percentages

- Never `toFixed()` on a raw API number in a component. Use the shared
  formatters in `src/lib/format/`.
- Always render the currency; a bare number in a multi-currency portfolio is
  ambiguous.
- Gains and losses need a sign and an accessible label, not colour alone.
  Colour-only encoding fails for colour-blind users.
- Never show a stale value as if it were live. Loading, empty, error, and
  stale-price are four distinct states and each needs a visible treatment.

### Accessibility and quality

- Semantic HTML first. Every interactive element is reachable and operable by
  keyboard.
- Every image and icon-only button has an accessible name.
- Tables of holdings are real `<table>` elements with headers, not `<div>` grids.
- Hold the UI to pixel-level care: consistent spacing scale, aligned numeric
  columns (right-aligned, tabular figures), no layout shift on data load.

### Configuration, not hardcoded values

There is one configuration root for this layer: **`src/lib/config.ts`**. Every
tunable value in the frontend is declared there and imported from there.

Tunable means anything someone could reasonably want to change without
rewriting logic: the API base URL, timeouts, retry counts, polling and refresh
intervals, page sizes, chart point limits, default locale and display currency,
feature flags, external URLs.

- **No magic numbers or magic strings** in components, hooks, or the API client.
  A bare `50` in a page is a decision nobody can find again, and a bare
  `"http://localhost:8000"` is a decision that breaks in production.
- `config.ts` is organised into **named sections, one per concern**, each
  carrying a comment stating what the section affects and who consumes it. A flat
  bag of unrelated constants stops being navigable at around twenty entries.
- Values are typed and validated once at module load - see
  [src/lib/AGENTS.md](src/lib/AGENTS.md) for the mechanics.
- **Stale configuration is deleted.** When an entry's last consumer goes away,
  the entry goes with it in the same change. Entries nobody reads make the file
  untrustworthy, and an untrustworthy config file gets bypassed with a literal.
- Only `NEXT_PUBLIC_*` variables reach the browser. **Never put a secret behind
  that prefix** - it is compiled into the bundle and shipped to every user.
- `config.ts` is the only file that reads `process.env`. Do not scatter it.

Design tokens are the styling equivalent and live in `src/app/globals.css`:
colour, spacing scale, type scale, radii. The same three rules apply - group
them by concern, never write an ad-hoc literal in a component's styles, and
delete tokens that nothing references.

---

## 5. Talking to the backend

All HTTP access goes through the typed client in `src/lib/api/`. No `fetch` in a
component, page, or hook.

Response shapes are declared as TypeScript types in `src/lib/api/types.ts` and
validated at the boundary. The backend is the source of truth for those shapes:
its OpenAPI schema is served at `http://localhost:8000/openapi.json` and browsable
at `http://localhost:8000/docs`.

**This is the one sanctioned cross-layer read.** When a contract is unclear,
read `app/server/app/api_contracts/` to confirm the shape - read-only. Do not
edit server files from a frontend task. If the contract itself is wrong, that is
a coordinated change: raise it, then change both sides in one commit.

Current API surface is rooted at `/users/{user_id}/portfolio`.

---

## 6. Verification

```bash
cd app/client && npm run lint && npm run test && npm run build
```

Run from `app/client`, never the repository root - this layer has its own
`package.json`.

`npm run build` catches type errors and Server/Client Component boundary
violations that `dev` tolerates. Run it before declaring a change done.

For anything user-visible, also load it in the running app at
`http://localhost:3000` (`make dev` from the repository root) and look at it.
Check the empty state and the error state, not just the happy path.
