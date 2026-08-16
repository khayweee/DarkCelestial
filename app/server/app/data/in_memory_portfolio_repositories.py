from app.domain.models import PortfolioHolding, PortfolioTransaction
from app.domain.repositories import PortfolioHoldingRepository, PortfolioTransactionRepository


class InMemoryPortfolioHoldingRepository(PortfolioHoldingRepository):
    def __init__(self) -> None:
        self._holdings: dict[tuple[str, str], PortfolioHolding] = {}

    async def create(self, holding: PortfolioHolding) -> PortfolioHolding:
        self._holdings[(holding.owner_id, holding.id)] = holding
        return holding

    async def list_by_owner(self, owner_id: str) -> list[PortfolioHolding]:
        return [
            holding
            for (stored_owner_id, _), holding in self._holdings.items()
            if stored_owner_id == owner_id
        ]

    async def get_by_owner(self, owner_id: str, holding_id: str) -> PortfolioHolding | None:
        return self._holdings.get((owner_id, holding_id))

    async def update(self, holding: PortfolioHolding) -> PortfolioHolding:
        self._holdings[(holding.owner_id, holding.id)] = holding
        return holding

    async def delete_by_owner(self, owner_id: str, holding_id: str) -> bool:
        return self._holdings.pop((owner_id, holding_id), None) is not None


class InMemoryPortfolioTransactionRepository(PortfolioTransactionRepository):
    def __init__(self) -> None:
        self._transactions: dict[tuple[str, str], PortfolioTransaction] = {}

    async def create(self, transaction: PortfolioTransaction) -> PortfolioTransaction:
        self._transactions[(transaction.owner_id, transaction.id)] = transaction
        return transaction

    async def list_by_owner(self, owner_id: str) -> list[PortfolioTransaction]:
        return [
            transaction
            for (stored_owner_id, _), transaction in self._transactions.items()
            if stored_owner_id == owner_id
        ]

    async def list_by_holding(self, owner_id: str, holding_id: str) -> list[PortfolioTransaction]:
        return [
            transaction
            for (stored_owner_id, _), transaction in self._transactions.items()
            if stored_owner_id == owner_id and transaction.holding_id == holding_id
        ]

    async def get_by_owner(self, owner_id: str, transaction_id: str) -> PortfolioTransaction | None:
        return self._transactions.get((owner_id, transaction_id))

    async def update(self, transaction: PortfolioTransaction) -> PortfolioTransaction:
        self._transactions[(transaction.owner_id, transaction.id)] = transaction
        return transaction

    async def delete_by_owner(self, owner_id: str, transaction_id: str) -> bool:
        return self._transactions.pop((owner_id, transaction_id), None) is not None

    async def exists_for_holding(self, owner_id: str, holding_id: str) -> bool:
        return any(
            stored_owner_id == owner_id and transaction.holding_id == holding_id
            for (stored_owner_id, _), transaction in self._transactions.items()
        )
