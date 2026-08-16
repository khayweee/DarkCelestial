from copy import deepcopy
from datetime import date

from app.domain.models import (
    HoldingHasTransactionsError,
    HoldingNotFoundError,
    OversellError,
    PortfolioHolding,
    PortfolioTransaction,
    TransactionSide,
)
from app.domain.repositories import PortfolioHoldingRepository, PortfolioTransactionRepository


class PortfolioService:
    def __init__(
        self,
        holding_repository: PortfolioHoldingRepository,
        transaction_repository: PortfolioTransactionRepository,
    ) -> None:
        self._holding_repository = holding_repository
        self._transaction_repository = transaction_repository

    async def create_holding(
        self,
        owner_id: str,
        symbol: str,
        exchange: str,
        quantity: float,
        average_cost: float,
        currency: str,
        notes: str | None,
    ) -> PortfolioHolding:
        holding = PortfolioHolding.create(
            owner_id=owner_id,
            symbol=symbol,
            exchange=exchange,
            quantity=quantity,
            average_cost=average_cost,
            currency=currency,
            notes=notes,
        )
        return await self._holding_repository.create(holding)

    async def list_holdings(self, owner_id: str) -> list[PortfolioHolding]:
        return await self._holding_repository.list_by_owner(owner_id)

    async def get_holding(self, owner_id: str, holding_id: str) -> PortfolioHolding | None:
        return await self._holding_repository.get_by_owner(owner_id, holding_id)

    async def update_holding(
        self,
        owner_id: str,
        holding_id: str,
        symbol: str | None,
        exchange: str | None,
        quantity: float | None,
        average_cost: float | None,
        currency: str | None,
        notes: str | None,
    ) -> PortfolioHolding | None:
        holding = await self._holding_repository.get_by_owner(owner_id, holding_id)
        if holding is None:
            return None
        holding.update(
            symbol=symbol,
            exchange=exchange,
            quantity=quantity,
            average_cost=average_cost,
            currency=currency,
            notes=notes,
        )
        await self._holding_repository.update(holding)
        if quantity is not None or average_cost is not None:
            return await self._recompute_holding(owner_id=owner_id, holding_id=holding_id)
        return holding

    async def delete_holding(self, owner_id: str, holding_id: str) -> bool:
        holding = await self._holding_repository.get_by_owner(owner_id, holding_id)
        if holding is None:
            return False
        if await self._transaction_repository.exists_for_holding(owner_id, holding_id):
            raise HoldingHasTransactionsError("Cannot delete a holding with transactions")
        return await self._holding_repository.delete_by_owner(owner_id, holding_id)

    async def create_transaction(
        self,
        owner_id: str,
        holding_id: str,
        side: TransactionSide,
        trade_date: date,
        quantity: float,
        price: float,
        currency: str,
        fees: float,
        notes: str | None,
    ) -> PortfolioTransaction:
        holding = await self._holding_repository.get_by_owner(owner_id, holding_id)
        if holding is None:
            raise HoldingNotFoundError("Holding not found")
        transaction = PortfolioTransaction.create(
            owner_id=owner_id,
            holding_id=holding_id,
            symbol=holding.symbol,
            side=side,
            trade_date=trade_date,
            quantity=quantity,
            price=price,
            currency=currency,
            fees=fees,
            notes=notes,
        )
        await self._transaction_repository.create(transaction)
        try:
            await self._recompute_holding(owner_id=owner_id, holding_id=holding_id)
        except OversellError:
            await self._transaction_repository.delete_by_owner(owner_id, transaction.id)
            raise
        return transaction

    async def list_transactions(self, owner_id: str) -> list[PortfolioTransaction]:
        return await self._transaction_repository.list_by_owner(owner_id)

    async def get_transaction(
        self,
        owner_id: str,
        transaction_id: str,
    ) -> PortfolioTransaction | None:
        return await self._transaction_repository.get_by_owner(owner_id, transaction_id)

    async def update_transaction(
        self,
        owner_id: str,
        transaction_id: str,
        side: TransactionSide | None,
        trade_date: date | None,
        quantity: float | None,
        price: float | None,
        currency: str | None,
        fees: float | None,
        notes: str | None,
    ) -> PortfolioTransaction | None:
        transaction = await self._transaction_repository.get_by_owner(owner_id, transaction_id)
        if transaction is None:
            return None
        previous_transaction = deepcopy(transaction)
        transaction.update(
            side=side,
            trade_date=trade_date,
            quantity=quantity,
            price=price,
            currency=currency,
            fees=fees,
            notes=notes,
        )
        updated = await self._transaction_repository.update(transaction)
        try:
            await self._recompute_holding(owner_id=owner_id, holding_id=updated.holding_id)
        except OversellError:
            await self._transaction_repository.update(previous_transaction)
            await self._recompute_holding(owner_id=owner_id, holding_id=previous_transaction.holding_id)
            raise
        return updated

    async def delete_transaction(self, owner_id: str, transaction_id: str) -> bool:
        transaction = await self._transaction_repository.get_by_owner(owner_id, transaction_id)
        if transaction is None:
            return False
        deleted = await self._transaction_repository.delete_by_owner(owner_id, transaction_id)
        if deleted:
            await self._recompute_holding(owner_id=owner_id, holding_id=transaction.holding_id)
        return deleted

    async def _recompute_holding(self, owner_id: str, holding_id: str) -> PortfolioHolding:
        holding = await self._holding_repository.get_by_owner(owner_id, holding_id)
        if holding is None:
            raise HoldingNotFoundError("Holding not found")
        transactions = await self._transaction_repository.list_by_holding(owner_id, holding_id)
        transactions = sorted(transactions, key=lambda item: (item.trade_date, item.created_at, item.id))
        quantity = holding.initial_quantity
        average_cost = holding.initial_average_cost
        for transaction in transactions:
            if transaction.side == TransactionSide.BUY:
                total_cost = (quantity * average_cost) + (transaction.quantity * transaction.price) + transaction.fees
                quantity += transaction.quantity
                average_cost = total_cost / quantity if quantity else 0.0
            else:
                if transaction.quantity > quantity:
                    raise OversellError("Cannot sell more than the current holding quantity")
                quantity -= transaction.quantity
                if quantity == 0:
                    average_cost = 0.0
        updated_holding = holding.clone_with_position(quantity=quantity, average_cost=average_cost)
        return await self._holding_repository.update(updated_holding)
