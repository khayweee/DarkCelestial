# Investment Portfolio Tracker Product Vision

## Overview

This project will become an AI-native full stack application that helps individual investors track, understand, and improve their investment portfolios.

The initial focus is portfolio visibility: users should be able to record their investments, understand what they own, see where their money is allocated, and track gains, losses, and risk exposure over time. The application will start with stocks and exchange-listed tickers from the New York Stock Exchange and London Stock Exchange, with support for derivatives such as options.

Over time, the application will evolve from a tracking tool into an intelligent investment assistant. It will use company fundamentals, market data, technical indicators, portfolio context, and AI/ML-driven analysis to help users monitor holdings, identify risks, and evaluate rebalancing opportunities.

## Product Objectives

- Give users clear visibility into their investment portfolio.
- Track buy and sell activity for stocks, and later options and other derivatives.
- Show realized and unrealized gains and losses.
- Help users understand allocation by ticker, sector, geography, exchange, currency, and asset type.
- Surface portfolio risk exposure in a way that is understandable to individual investors.
- Provide company-level performance tracking and key metrics for each holding.
- Use AI to suggest relevant metrics, competitors, risks, and portfolio insights.
- Eventually support investment strategy modules powered by market data, technical analysis, AI, and ML.

## Target Users

The first target user is an individual investor who manages their own portfolio and wants better visibility than a spreadsheet provides.

This user may hold positions across US and UK listed stocks, may trade periodically, and may later want to track derivatives such as options. They are interested not only in what they own, but also in how those investments are performing, what risks they are taking, and whether their portfolio remains aligned with their strategy.

## Initial Scope

### Phase 1: Portfolio Tracking

The first module will allow users to record investment activity and view portfolio state.

Core capabilities:

- Add stock buy records.
- Add stock sell records.
- Track holdings by ticker.
- Support listed stocks from NYSE and LSE.
- Store transaction details such as ticker, exchange, trade date, quantity, price, currency, fees, and notes.
- Calculate current position quantity.
- Calculate average cost basis.
- Calculate realized gains and losses from sell records.
- Calculate unrealized gains and losses when market prices are available.
- Show portfolio value and allocation.
- Add options and other derivatives.
- Track option-specific fields such as contract type, strike price, expiration date, premium, multiplier, and assignment or exercise status.

### Phase 2: Performance Tracking

The second module will enrich each holding with company and market context.

Core capabilities:

- Show company profile and business summary.
- Track key financial and operating metrics for each company.
- Track valuation, growth, profitability, debt, and cash flow indicators.
- Identify relevant competitors.
- Compare a holding against competitors and sector benchmarks.
- Use AI to suggest important metrics for a company based on its industry and business model.
- Highlight notable changes in fundamentals, valuation, sentiment, or technical indicators.

Potential examples:

- Revenue growth.
- Earnings growth.
- Free cash flow.
- Gross margin and operating margin.
- Debt-to-equity ratio.
- Price-to-earnings ratio.
- Price-to-sales ratio.
- Dividend yield.
- Analyst sentiment.
- Relative performance versus competitors.

### Phase 3: Investment Strategy

The third module will introduce AI and ML-based strategy support.

Core capabilities:

- Analyze portfolio concentration and diversification.
- Detect overweight or underweight exposures.
- Recommend rebalancing opportunities.
- Identify technical signals and market trends.
- Suggest watchlist additions based on user strategy and current holdings.
- Use real-time or near-real-time market data where available.
- Explain recommendations in plain language, including assumptions and risks.

Important constraint:

The application should support investment analysis and decision-making, but should not present recommendations as guaranteed outcomes or personalized financial advice without appropriate safeguards, disclosures, and user controls.

## AI-Native Direction

AI should be part of the product experience from the beginning, but introduced carefully and iteratively.

Early AI use cases:

- Suggest tags and categories for holdings.
- Summarize a company and its business model.
- Suggest relevant performance metrics for a ticker.
- Identify competitors.
- Explain portfolio allocation and risk in plain language.
- Generate portfolio summaries and notable changes.

Later AI and ML use cases:

- Portfolio rebalancing suggestions.
- Technical analysis summaries.
- Opportunity detection.
- Risk alerts.
- Personalized strategy analysis.
- Scenario modeling.

AI outputs should be traceable to source data wherever possible. The product should distinguish between factual data, calculated metrics, model-generated interpretation, and user-facing recommendations.

## Data Requirements

The application will need several categories of data.

User-entered data:

- Transactions.
- Holdings.
- Notes.
- Watchlists.
- User preferences.
- Investment goals and strategy settings.

Market data:

- Ticker metadata.
- Exchange data.
- Current and historical prices.
- Currency exchange rates.
- Corporate actions such as splits and dividends.

Company data:

- Company profile.
- Financial statements.
- Key ratios.
- Sector and industry classification.
- Competitors.
- News and events.

AI and analysis data:

- Generated summaries.
- Suggested metrics.
- Risk explanations.
- Recommendation history.
- Model inputs and reasoning metadata where appropriate.

## Full Stack Direction

The application will be developed as a full stack system.

Expected areas:

- Frontend application for portfolio entry, dashboards, analysis views, and AI-assisted workflows.
- Backend API for portfolio records, calculations, market data integrations, and AI workflows.
- Database for user portfolios, transaction history, calculated state, and generated insights.
- Market data integration layer.
- AI analysis layer.
- Authentication and user account management.
- Background jobs for price refreshes, metric updates, alerts, and scheduled analysis.

## MVP Success Criteria

The first usable version should allow a user to:

- Add stock buy and sell transactions.
- View current holdings.
- See total invested amount and current portfolio value.
- See realized and unrealized gains and losses.
- Understand allocation across tickers and exchanges.
- Open a holding detail page with transaction history and basic performance information.

## Future Considerations

- Multi-currency support across USD, GBP, and other currencies.
- Tax lot accounting methods.
- Dividend tracking.
- Import from broker statements or CSV files.
- Watchlists.
- Alerts and notifications.
- Options and derivatives tracking.
- Portfolio benchmarking.
- Real-time market data subscriptions.
- Mobile-friendly experience.
- Data provider selection and cost.
- Security and privacy requirements.
- Regulatory and financial advice disclaimers.

## Open Questions

- Should the first version support only one user locally, or include full authentication from the start?
- Which market data provider should be used for NYSE and LSE coverage?
- Should prices be refreshed manually, scheduled, or both?
- What cost basis method should be used first?
- Should the MVP include multi-currency conversion immediately?
- Should options be included in the initial data model even if the UI comes later?
- What level of AI explanation is required before showing recommendation-like insights?
- Should recommendations be framed as educational insights, portfolio observations, or explicit suggested actions?

