# AGENTS.md - Routes (`app/client/src/app`)

**Parent:** [app/client/AGENTS.md](../../AGENTS.md). Read it first for the
stack, the Server Component policy, and the formatting rules.

**Scope:** the App Router tree - routes, layouts, loading and error boundaries,
and global styles.

**This directory is the app's page list.** Per the parent file, `src/app/` is
where pages live; there is no `pages/` directory and creating one is a bug.

---

## What belongs here

Routing and composition only. A page decides *what the user is looking at* and
assembles components to show it.

A page should be short. If it contains substantial markup, that markup is a
component. If it contains logic, that logic is a hook or a `lib` function. A
page that has grown past composition usually wants one feature component named
after the view - `<HoldingsView />` in `components/features/holdings/` - which
the page renders with the data it fetched.

## What does not belong here

- Reusable UI - it goes in `src/components/`.
- Data fetching implementation - it goes through the typed client in
  `src/lib/api/`.
- Any financial calculation. The API returns computed values; pages display
  them.
- Anything imported by a sibling route. Cross-route imports are the signal that
  something belongs in `components/`, `hooks/`, or `lib/`.

## Server Components

Pages and layouts are Server Components. Fetch data there, on the server, and
pass it down.

Add `'use client'` only in a leaf that truly needs interactivity, and never in
`layout.tsx` or a page that has interactive children - it opts the whole subtree
out of server rendering.

## Required states

A portfolio route is never just a happy path. Every data-backed route provides
all four, and each is visibly distinct:

| State | Mechanism |
|---|---|
| Loading | `loading.tsx`, with a skeleton that matches the final layout so nothing shifts |
| Error | `error.tsx`, recoverable, with a retry - never a blank screen |
| Empty | Handled in the page: a new user with no holdings sees guidance, not an empty table |
| Stale | Prices carry an "as of" time; never render a stale number as if it were live |

## Structure

```
src/app/
├── layout.tsx        Root shell: html, body, providers, global chrome
├── page.tsx          Portfolio overview
├── globals.css       Design tokens and resets only
└── <segment>/        One page of the product
    ├── page.tsx
    ├── loading.tsx
    └── error.tsx
```

Route segments are named for what the user sees - `holdings`, `transactions`,
`performance` - and mirror the product's language, not the backend's table
names. One segment is one page; the segment name is the URL, so renaming it
breaks bookmarks.

Reach for the App Router's own tools before inventing structure:

- **Nested `layout.tsx`** for chrome shared by a group of pages. It does not
  re-render on navigation between its children, so state inside it survives.
- **Route groups `(name)/`** to organise segments without adding a URL path
  part - use them when the file tree needs grouping the URL should not show.
- **Dynamic segments `[id]/`** for entity pages, with the id treated as an
  opaque string. Note that `params` and `searchParams` are async and must be
  awaited.

## Navigation

The parent file sets the rule: internal navigation is client-side, via `<Link>`
or `useRouter`. `window.location` counts as a full reload too.

`useRouter`, `usePathname`, and `useSearchParams` are client-only. A layout or
page that imports one becomes a Client Component along with its whole subtree,
so put them in a small `'use client'` leaf - a nav item that needs to know
whether it is active, not the nav.

## Metadata and styling

- Every route exports `metadata` with a real title. It is the browser tab and
  the accessibility landmark.
- `globals.css` holds design tokens, resets, and base typography. Component
  styling lives with the component. Do not accumulate page-specific rules in
  `globals.css`.

## Migration note

`layout.jsx` and `page.jsx` are the placeholder "Trading Assistant" WebSocket
dashboard from an earlier product direction. They are **not** a pattern to
follow - the page holds a raw `WebSocket`, inline styles, and display logic all
at once. Replace them when the first real portfolio route lands, and write new
files as `.tsx`.
