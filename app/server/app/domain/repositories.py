from typing import Protocol

from app.domain.models import PortfolioHolding, PortfolioTransaction


class PortfolioHoldingRepository(Protocol):
    async def create(self, holding: PortfolioHolding) -> PortfolioHolding:
        ...

    async def list_by_owner(self, owner_id: str) -> list[PortfolioHolding]:
        ...

    async def get_by_owner(self, owner_id: str, holding_id: str) -> PortfolioHolding | None:
        ...

    async def update(self, holding: PortfolioHolding) -> PortfolioHolding:
        ...

    async def delete_by_owner(self, owner_id: str, holding_id: str) -> bool:
        ...


class PortfolioTransactionRepository(Protocol):
    async def create(self, transaction: PortfolioTransaction) -> PortfolioTransaction:
        ...

    async def list_by_owner(self, owner_id: str) -> list[PortfolioTransaction]:
        ...

    async def list_by_holding(self, owner_id: str, holding_id: str) -> list[PortfolioTransaction]:
        ...

    async def get_by_owner(self, owner_id: str, transaction_id: str) -> PortfolioTransaction | None:
        ...

    async def update(self, transaction: PortfolioTransaction) -> PortfolioTransaction:
        ...

    async def delete_by_owner(self, owner_id: str, transaction_id: str) -> bool:
        ...

    async def exists_for_holding(self, owner_id: str, holding_id: str) -> bool:
        ...
