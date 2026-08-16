# Dev/Prod System Architecture

## Summary

This project is an AI-native investment portfolio tracker. The architecture should support cheap local development for two collaborators while keeping a clear path to production-grade cloud deployment.

Local development uses Docker Compose and local service equivalents where practical. Staging and production use AWS managed services. Staging should mirror production as closely as possible, with differences limited to scale, budgets, retention, backup settings, and high-availability choices.

The key pattern is provider abstraction. Application code should talk to internal interfaces such as `AIProvider`, `MarketDataProvider`, and storage, cache, and database clients. Environment configuration selects the implementation, so moving between dev, staging, and production is a configuration change rather than a code change.

Backend code should follow the layered architecture documented in `app/server/docs/presentation-domain-data.md`: Presentation calls the Service/Application layer, the Service/Application layer coordinates domain models and repository interfaces, and Data implementations satisfy those domain interfaces.

## Service Table

| Service | Dev | Prod / Staging | Purpose |
|---|---|---|---|
| Frontend web app | Next.js in Docker Compose on `localhost:3000`; browser API calls go to Nginx at `localhost:8000` | AWS Amplify Hosting or ECS/Fargate behind CloudFront; browser API calls go to the public API domain | Desktop-first web UI, built responsive/mobile-native from the start |
| Web server / reverse proxy | Nginx container exposed on `localhost:8000` for local multi-service routing | CloudFront plus optional Nginx only if self-managed proxy behavior is needed | Serve static assets where applicable, terminate/proxy HTTP traffic, and route frontend/API paths |
| API gateway / API entry point | Nginx reverse proxy on `localhost:8000` for path-based local API routing | Amazon API Gateway or Application Load Balancer, depending on API-management needs | Public API front door for routing, auth checks, throttling, request policies, and service fan-out |
| Application server (Backend) | FastAPI services running on Uvicorn in Docker Compose, reachable through Nginx rather than directly from the browser | FastAPI services running on Uvicorn in ECS Fargate behind the API entry point | Execute backend business logic, validation, portfolio calculations, provider orchestration, and database/cache access |
| Database | PostgreSQL container | Amazon RDS PostgreSQL | Store users, transactions, holdings, calculated portfolio state, AI metadata |
| Cache / broker | Redis container | Amazon ElastiCache Redis | Cache market data, rate-limit state, background job queue broker |
| Background jobs | Worker container using same backend image | ECS Fargate worker service | Price refreshes, metric updates, summaries, scheduled AI analysis |
| Object storage | MinIO container or local filesystem | Amazon S3 | Store imports, reports, generated artifacts, future broker statement uploads |
| Auth | Local dev auth mode or Cognito test pool | Amazon Cognito | User accounts, login, JWT validation, future mobile auth compatibility |
| Secrets | `.env.local` and ignored local secret files | AWS Secrets Manager / SSM Parameter Store | Store database credentials, provider keys, Bedrock config, market data keys |
| AI model provider | Ollama local LLM server | Amazon Bedrock via AWS SDK | Cheap local AI experimentation; managed production AI inference |
| AI provider adapter | Internal backend adapter targeting Ollama HTTP API | Same adapter interface targeting Bedrock runtime | Keep AI workflows environment-switchable |
| Vector / semantic search | Postgres `pgvector` extension locally | RDS PostgreSQL with `pgvector`, later OpenSearch if needed | Store embeddings and retrieved AI context |
| Market data | `yfinance`, mock provider, or low-cost API | Paid/free market data provider selected by config | Prices, ticker metadata, fundamentals, FX rates |
| Observability logs | Docker Compose logs | CloudWatch Logs | Debugging and service visibility |
| Metrics / traces | Optional local OpenTelemetry collector | CloudWatch metrics + OpenTelemetry / AWS X-Ray | Latency, job health, provider call visibility |
| Error monitoring | Local logs only | Sentry or CloudWatch alarms | Capture frontend/backend runtime exceptions |
| Email / notifications | Mailhog container or disabled provider | Amazon SES | Account emails, alerts, reports, future notifications |
| Container registry | Local Docker images | Amazon ECR | Store versioned frontend/backend/worker images |
| CI/CD | Local commands plus GitHub Actions checks | GitHub Actions deploying to AWS via OIDC | Build, test, scan, push images, Terraform plan/apply |
| Infrastructure as Code | Docker Compose; optional LocalStack for selected AWS services | Terraform AWS provider with staging/prod variable files | Repeatable cloud provisioning with environment-specific config |
| Mobile app path | Shared API contract and responsive web UI | Same backend/auth/API services; future React Native/Expo app | Keep mobile-native path open without building mobile now |

## Key Practices

### Config-Driven Environment Switching

Use environment-specific configuration files and typed runtime settings:

- App config: `.env.local`, `.env.dev`, `.env.staging`, `.env.prod`.
- Infrastructure config: Terraform modules plus `staging.tfvars` and `prod.tfvars`.
- Example runtime flags: `AI_PROVIDER=ollama|bedrock`, `AI_MODEL`, `OLLAMA_BASE_URL`, `AWS_REGION`, `BEDROCK_MODEL_ID`.

Runtime code should depend on configuration values and internal interfaces, not direct environment checks scattered through business logic.

### Cheap Local Development

Local development should avoid mandatory paid cloud services:

- Run Ollama locally or as a Docker-accessible host service.
- Use small local models for AI-assisted development workflows.
- Use mock AI responses for deterministic tests.
- Use Docker Compose for local app, database, cache, and optional supporting services.
- Avoid requiring Bedrock, RDS, ElastiCache, Cognito, or other paid AWS services for ordinary feature work.

### Production AI With Bedrock

Staging and production should use Amazon Bedrock directly at first:

- The backend calls Bedrock Runtime through an AI provider adapter.
- Bedrock credentials and model configuration are stored in AWS Secrets Manager or SSM Parameter Store.
- Bedrock Agents and Knowledge Bases are not part of the initial architecture.
- Add Bedrock Agents, Knowledge Bases, or AWS-native retrieval later only when product workflows require managed retrieval, multi-step agents, or managed knowledge stores.

### Terraform Usage

Use Terraform where it adds real operational value:

- Provision AWS networking, ECS, RDS, ElastiCache, S3, Cognito, Secrets Manager, IAM, CloudWatch, ECR, DNS, and TLS.
- Keep reusable Terraform modules shared by staging and production.
- Keep separate Terraform state per environment.
- Use environment variable files for settings such as instance sizes, retention, domain names, backup windows, deletion protection, and high-availability settings.
- Keep Docker Compose as the main local developer experience.
- Use LocalStack only for selected AWS workflows where local emulation is worth the setup cost.

## Test / Acceptance Plan

- Confirm this document contains a `service`, `dev`, `prod`, `purpose` table.
- Confirm AI provider choices are explicitly Ollama for dev and Amazon Bedrock for staging/prod.
- Confirm staging is documented as production-equivalent except for scale, budgets, retention, and high-availability settings.
- Confirm the document explains config-driven switching and does not require code changes between environments.
- Confirm this first step changes documentation only.

## Assumptions

- Cloud provider: AWS.
- Local LLM server: Ollama.
- Production AI provider: direct Amazon Bedrock Runtime through a backend adapter.
- Dev/prod parity style: pragmatic parity, prioritizing low local cost and simple onboarding for two collaborators.
- First document scope: MVP plus near-future services needed for an AI-native portfolio tracker.
