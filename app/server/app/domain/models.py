from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from enum import Enum
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TransactionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PortfolioError(Exception):
    pass


class HoldingNotFoundError(PortfolioError):
    pass


class TransactionNotFoundError(PortfolioError):
    pass


class OversellError(PortfolioError):
    pass


class HoldingHasTransactionsError(PortfolioError):
    pass


@dataclass
class PortfolioHolding:
    id: str
    owner_id: str
    symbol: str
    exchange: str
    quantity: float
    average_cost: float
    initial_quantity: float
    initial_average_cost: float
    currency: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        owner_id: str,
        symbol: str,
        exchange: str,
        quantity: float,
        average_cost: float,
        currency: str,
        notes: str | None,
    ) -> "PortfolioHolding":
        now = utc_now()
        return cls(
            id=str(uuid4()),
            owner_id=owner_id,
            symbol=normalize_symbol(symbol),
            exchange=normalize_exchange(exchange),
            quantity=quantity,
            average_cost=average_cost,
            initial_quantity=quantity,
            initial_average_cost=average_cost,
            currency=normalize_currency(currency),
            notes=notes,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        symbol: str | None = None,
        exchange: str | None = None,
        quantity: float | None = None,
        average_cost: float | None = None,
        currency: str | None = None,
        notes: str | None = None,
    ) -> None:
        if symbol is not None:
            self.symbol = normalize_symbol(symbol)
        if exchange is not None:
            self.exchange = normalize_exchange(exchange)
        if quantity is not None:
            self.quantity = quantity
            self.initial_quantity = quantity
        if average_cost is not None:
            self.average_cost = average_cost
            self.initial_average_cost = average_cost
        if currency is not None:
            self.currency = normalize_currency(currency)
        if notes is not None:
            self.notes = notes
        self.updated_at = utc_now()

    def clone_with_position(self, quantity: float, average_cost: float) -> "PortfolioHolding":
        return replace(
            self,
            quantity=quantity,
            average_cost=average_cost,
            updated_at=utc_now(),
        )


@dataclass
class PortfolioTransaction:
    id: str
    owner_id: str
    holding_id: str
    symbol: str
    side: TransactionSide
    trade_date: date
    quantity: float
    price: float
    currency: str
    fees: float
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        owner_id: str,
        holding_id: str,
        symbol: str,
        side: TransactionSide,
        trade_date: date,
        quantity: float,
        price: float,
        currency: str,
        fees: float,
        notes: str | None,
    ) -> "PortfolioTransaction":
        now = utc_now()
        return cls(
            id=str(uuid4()),
            owner_id=owner_id,
            holding_id=holding_id,
            symbol=normalize_symbol(symbol),
            side=side,
            trade_date=trade_date,
            quantity=quantity,
            price=price,
            currency=normalize_currency(currency),
            fees=fees,
            notes=notes,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        side: TransactionSide | None = None,
        trade_date: date | None = None,
        quantity: float | None = None,
        price: float | None = None,
        currency: str | None = None,
        fees: float | None = None,
        notes: str | None = None,
    ) -> None:
        if side is not None:
            self.side = side
        if trade_date is not None:
            self.trade_date = trade_date
        if quantity is not None:
            self.quantity = quantity
        if price is not None:
            self.price = price
        if currency is not None:
            self.currency = normalize_currency(currency)
        if fees is not None:
            self.fees = fees
        if notes is not None:
            self.notes = notes
        self.updated_at = utc_now()


def normalize_symbol(value: str) -> str:
    return value.strip().upper()


def normalize_exchange(value: str) -> str:
    return value.strip().upper()


def normalize_currency(value: str) -> str:
    return value.strip().upper()
