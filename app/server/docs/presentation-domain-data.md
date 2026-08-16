# Backend Layered Architecture

This backend follows an inward-facing Domain-Driven Design style inspired by
Martin Fowler's enterprise application architecture patterns. The first bounded
context is portfolio tracking: users can manage stock holdings and buy/sell
transactions while the backend keeps current holding state consistent.

The dependency direction is:

~~~text
Presentation -> Service/Application -> Domain <- Data
~~~

Outer layers may depend on inner abstractions. Inner layers must not import
outer implementation details. The domain layer stays at the center and does not
know about FastAPI, Pydantic API DTOs, SQLAlchemy, market-data clients, or
concrete repository implementations.

## Layer Responsibilities

### Presentation Layer

Location:

- `app/api`
- `app/api_contracts`
- `app/dependencies.py`

Responsibilities:

- Define FastAPI routers, HTTP paths, status codes, and error mapping.
- Own Pydantic request and response DTOs in `api_contracts`.
- Expose portfolio routes under `/users/{user_id}/portfolio`.
- Convert HTTP input into service/application calls.
- Convert service results and domain/application errors into API responses.
- Wire concrete dependencies for FastAPI injection.

This layer should not contain persistence code, SQL/ORM models, market-data
logic, or business workflows.

### Service/Application Layer

Location:

- `app/service`

Responsibilities:

- Own use-case services such as `PortfolioService`.
- Coordinate portfolio workflows across holdings, transactions, and repository
  interfaces.
- Keep transactions and current holding state consistent.
- Provide a stable boundary for presentation code to call.
- Later, own transaction boundaries or unit-of-work coordination when real
  persistence is introduced.

This layer may use domain entities and domain repository interfaces. It should
not depend on FastAPI, Pydantic API contracts, or concrete database adapters.

### Domain Layer

Location:

- `app/domain`

Responsibilities:

- Own business entities such as `PortfolioHolding` and
  `PortfolioTransaction`.
- Own business terms such as `TransactionSide` and domain/application errors
  such as oversell or protected-delete failures.
- Own business rules that are true regardless of API or storage.
- Own repository interfaces, expressed as protocols.
- Later, own derivatives-specific value objects and rules when that bounded
  context becomes real.

Current simple rules:

- Portfolio data is path-scoped by `owner_id`; there is no auth or users table
  yet.
- V1 holdings are stock-only, but the API uses portfolio language so derivatives
  can be added later.
- Symbols, exchanges, and currencies are normalized to uppercase.
- Buy transactions increase quantity and weighted average cost.
- Sell transactions decrease quantity and cannot exceed the current holding
  quantity.
- Holdings with transaction history cannot be deleted silently.

The domain layer must remain independent of all framework, transport, and
storage implementation details.

### Data Layer

Location:

- `app/data`

Responsibilities:

- Implement domain repository protocols.
- Own persistence details such as database sessions, ORM mappings, and query
  code when a database is introduced.
- Translate between storage records and domain models.
- Keep data-access implementation details behind interfaces used by the service
  and domain layers.

Current implementation:

- `InMemoryPortfolioHoldingRepository` stores holdings by
  `(owner_id, holding_id)`.
- `InMemoryPortfolioTransactionRepository` stores transactions by
  `(owner_id, transaction_id)` and can list transactions for one holding.

Future implementation:

- Database repositories can implement the same portfolio repository protocols.
- ORM models should live under `app/data`, not in `app/domain` or
  `app/api_contracts`.
- Migration tooling should be added only when real database tables are
  introduced.

## Request Flow

~~~text
HTTP request
  -> app/api/portfolio.py
  -> app/api_contracts/portfolio.py
  -> app/service/portfolio_service.py
  -> app/domain/repositories.py
  -> app/data/in_memory_portfolio_repositories.py
  -> domain model returned
  -> API response
~~~

Dependency wiring:

~~~text
app/dependencies.py
  -> creates concrete repository implementations
  -> injects them into service/application objects
  -> exposes FastAPI dependency functions
~~~

## Server Structure

~~~text
app/server/
  app/
    main.py
    dependencies.py
    api/
      portfolio.py
    api_contracts/
      portfolio.py
    service/
      portfolio_service.py
    domain/
      models.py
      repositories.py
    data/
      in_memory_portfolio_repositories.py
  docs/
    presentation-domain-data.md
~~~

## Naming Guidance

- Use `api_contracts` for Pydantic request and response DTOs.
- Use `service/*_service.py` for use cases and application workflows.
- Use `domain/models.py` for business entities and small domain terms.
- Use `domain/repositories.py` for repository protocols.
- Use `data/*_repository.py` for concrete persistence implementations.
- Use `data/models.py` later for ORM/database models, not API contracts.

## What Not to Add Yet

Do not add these until the portfolio CRUD model is stable:

- authentication and a users table
- SQLAlchemy or database migrations
- `yfinance`
- `ta`
- market-data streaming
- trading signal services
- indicator calculation services
- WebSocket broadcasting

Those features are useful later, but they introduce more infrastructure and
bounded contexts. Keeping them out for now makes the stock portfolio model
easier to design, test, and persist.
