from app.data.in_memory_portfolio_repositories import (
    InMemoryPortfolioHoldingRepository,
    InMemoryPortfolioTransactionRepository,
)
from app.service.portfolio_service import PortfolioService

holding_repository = InMemoryPortfolioHoldingRepository()
transaction_repository = InMemoryPortfolioTransactionRepository()
portfolio_service = PortfolioService(
    holding_repository=holding_repository,
    transaction_repository=transaction_repository,
)


def get_portfolio_service() -> PortfolioService:
    return portfolio_service
