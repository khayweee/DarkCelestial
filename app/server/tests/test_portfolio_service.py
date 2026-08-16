import asyncio
from datetime import date

import pytest

from app.data.in_memory_portfolio_repositories import (
    InMemoryPortfolioHoldingRepository,
    InMemoryPortfolioTransactionRepository,
)
from app.domain.models import HoldingHasTransactionsError, OversellError, TransactionSide
from app.service.portfolio_service import PortfolioService


def make_portfolio_service() -> PortfolioService:
    return PortfolioService(
        holding_repository=InMemoryPortfolioHoldingRepository(),
        transaction_repository=InMemoryPortfolioTransactionRepository(),
    )


def test_holdings_are_scoped_by_owner() -> None:
    async def scenario() -> None:
        portfolio_service = make_portfolio_service()
        alice_holding = await portfolio_service.create_holding(
            owner_id="alice",
            symbol="aapl",
            exchange="nasdaq",
            quantity=10,
            average_cost=100,
            currency="usd",
            notes=None,
        )
        await portfolio_service.create_holding(
            owner_id="bob",
            symbol="msft",
            exchange="nasdaq",
            quantity=5,
            average_cost=200,
            currency="usd",
            notes=None,
        )

        alice_holdings = await portfolio_service.list_holdings(owner_id="alice")
        bob_cannot_read_alice = await portfolio_service.get_holding(
            owner_id="bob",
            holding_id=alice_holding.id,
        )

        assert [holding.symbol for holding in alice_holdings] == ["AAPL"]
        assert bob_cannot_read_alice is None

    asyncio.run(scenario())


def test_buy_transaction_increases_quantity_and_weighted_average_cost() -> None:
    async def scenario() -> None:
        portfolio_service = make_portfolio_service()
        holding = await portfolio_service.create_holding(
            owner_id="alice",
            symbol="AAPL",
            exchange="NASDAQ",
            quantity=10,
            average_cost=100,
            currency="USD",
            notes=None,
        )

        await portfolio_service.create_transaction(
            owner_id="alice",
            holding_id=holding.id,
            side=TransactionSide.BUY,
            trade_date=date(2026, 1, 1),
            quantity=5,
            price=120,
            currency="USD",
            fees=5,
            notes=None,
        )

        updated_holding = await portfolio_service.get_holding("alice", holding.id)

        assert updated_holding is not None
        assert updated_holding.quantity == 15
        assert updated_holding.average_cost == pytest.approx(107)

    asyncio.run(scenario())


def test_sell_transaction_decreases_quantity() -> None:
    async def scenario() -> None:
        portfolio_service = make_portfolio_service()
        holding = await portfolio_service.create_holding(
            owner_id="alice",
            symbol="AAPL",
            exchange="NASDAQ",
            quantity=10,
            average_cost=100,
            currency="USD",
            notes=None,
        )

        await portfolio_service.create_transaction(
            owner_id="alice",
            holding_id=holding.id,
            side=TransactionSide.SELL,
            trade_date=date(2026, 1, 2),
            quantity=4,
            price=130,
            currency="USD",
            fees=0,
            notes=None,
        )

        updated_holding = await portfolio_service.get_holding("alice", holding.id)

        assert updated_holding is not None
        assert updated_holding.quantity == 6
        assert updated_holding.average_cost == 100

    asyncio.run(scenario())


def test_oversell_rejects_transaction_and_keeps_holding_unchanged() -> None:
    async def scenario() -> None:
        portfolio_service = make_portfolio_service()
        holding = await portfolio_service.create_holding(
            owner_id="alice",
            symbol="AAPL",
            exchange="NASDAQ",
            quantity=3,
            average_cost=100,
            currency="USD",
            notes=None,
        )

        with pytest.raises(OversellError):
            await portfolio_service.create_transaction(
                owner_id="alice",
                holding_id=holding.id,
                side=TransactionSide.SELL,
                trade_date=date(2026, 1, 3),
                quantity=4,
                price=130,
                currency="USD",
                fees=0,
                notes=None,
            )

        transactions = await portfolio_service.list_transactions("alice")
        updated_holding = await portfolio_service.get_holding("alice", holding.id)

        assert transactions == []
        assert updated_holding is not None
        assert updated_holding.quantity == 3
        assert updated_holding.average_cost == 100

    asyncio.run(scenario())


def test_delete_holding_with_transactions_is_rejected() -> None:
    async def scenario() -> None:
        portfolio_service = make_portfolio_service()
        holding = await portfolio_service.create_holding(
            owner_id="alice",
            symbol="AAPL",
            exchange="NASDAQ",
            quantity=1,
            average_cost=100,
            currency="USD",
            notes=None,
        )
        await portfolio_service.create_transaction(
            owner_id="alice",
            holding_id=holding.id,
            side=TransactionSide.BUY,
            trade_date=date(2026, 1, 4),
            quantity=1,
            price=100,
            currency="USD",
            fees=0,
            notes=None,
        )

        with pytest.raises(HoldingHasTransactionsError):
            await portfolio_service.delete_holding("alice", holding.id)

    asyncio.run(scenario())
