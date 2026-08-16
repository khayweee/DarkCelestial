# dark-celestial

An AI-native investment portfolio tracker for individual investors. Users
record what they own and what they traded, and the product explains how the
portfolio is actually performing and where its risk sits.

## Setup

### Prerequisites

- Docker and Docker Compose
- [GitHub CLI (`gh`)](https://cli.github.com/) - this repo tracks
  implementation work via GitHub issues, so `gh` is required for contributors.

### 1. Check your tooling

```bash
make setup_repo
```

Verifies required local tooling (currently just `gh`) is installed, via
`scripts/setup.sh`.

### 2. Start the app

```bash
make dev
```

Starts both services with hot reload:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`

## Learn more

- [AGENTS.md](./AGENTS.md) - repository conventions and engineering rules.
- [docs/](./docs) - deeper architecture and product context, including
  [docs/product-vision.md](./docs/product-vision.md),
  [docs/system-architecture.md](./docs/system-architecture.md), and
  [docs/databaseformultipleusers.md](./docs/databaseformultipleusers.md).
