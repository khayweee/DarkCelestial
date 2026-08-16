# AGENTS.md - AI research layer (`app/server/app/agents`)

**Parent:** [app/server/AGENTS.md](../../AGENTS.md). Read it first for the
layering rule and backend conventions.

**Scope:** LangChain / LangGraph workflows that explain portfolio exposure,
risk, and opportunities.

> **Status: not yet implemented.** This directory currently holds only its
> instructions. It exists so the boundary is decided before the first line of
> code, not after. Do not create modules here without a story that calls for
> them - see "Not yet in scope" in the parent file.

---

## Position in the architecture

This is a **bounded context inside the backend**, not a separate service. It
reuses the same configuration, the same data access, and the same deployment
unit.

For layering purposes it sits alongside the application layer:

- **May import:** `app/domain/` and `app/service/` (to read portfolio state
  through existing use cases).
- **Must not import:** `app/api/`, `app/api_contracts/`, or a concrete
  repository from `app/data/`.
- **Nothing else imports it** except `app/api/`, which exposes its results over
  HTTP like any other use case.

The domain stays free of LangChain. An agent workflow is an application-level
concern that consumes domain objects; it never becomes one.

## The provider rule

LangChain talks to a model through **our** interface, not the other way round.

- Model access goes through an `AIProvider` adapter implemented in `app/data/`.
- Ollama locally, Amazon Bedrock in staging and production, selected by
  configuration. See [docs/system-architecture.md](../../../../docs/system-architecture.md).
- Never import a vendor SDK or hardcode a model identifier in this directory.
- Never let a framework abstraction become the seam that survives - if LangGraph
  is replaced, everything outside this directory should be unaffected.

## Structure, when it lands

```
agents/
├── graphs/       LangGraph state machines, one per workflow
├── tools/        Tools the model may call
├── prompts/      Prompt templates, versioned
└── schemas.py    Typed inputs and outputs
```

## Non-negotiables for a financial AI feature

These are product requirements, not style preferences.

1. **Never let a model compute a number the deterministic code can compute.**
   CAGR, allocation weights, PnL, and concentration come from `app/service/` and
   are passed to the model as facts. A model that does arithmetic will
   eventually do it wrong, confidently, about someone's money.
2. **Separate the four kinds of content** in every output: source data,
   calculated metrics, model interpretation, and anything resembling a
   recommendation. The API must let the frontend render them differently.
3. **Every claim is traceable.** Outputs carry the inputs they were derived
   from. An unattributable assertion about a user's portfolio is not shippable.
4. **This is not financial advice.** Frame output as observation and
   explanation. Do not generate buy/sell instructions, price targets, or
   guaranteed outcomes without an explicit product decision and the
   corresponding disclosures.
5. **Tools are read-only.** A model-invoked tool may query portfolio state. It
   must never create, update, or delete a holding or transaction.
6. **Bound every run.** Explicit step, token, latency, and cost limits on each
   graph. An unbounded agent loop against a paid API is an availability and
   billing incident.

## Data handling

Portfolio holdings are sensitive personal financial data. Send the minimum
required to the provider, never log the full prompt or completion at info level,
and treat a third-party model endpoint as an external disclosure boundary -
document what leaves the system before it does.

## Testing

- **Deterministic by default.** Unit tests use a stub `AIProvider` with recorded
  responses. No test in the standard suite makes a live model call.
- Test the graph's control flow - branching, retries, termination, limit
  enforcement - independently of model output quality.
- Prompt and output quality get their own evaluation set, run deliberately, kept
  out of the fast feedback loop.
