from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.models import TransactionSide


class HoldingCreateRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    exchange: str = Field(min_length=1, max_length=20)
    quantity: float = Field(ge=0)
    average_cost: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("symbol", "exchange", "currency")
    @classmethod
    def normalize_uppercase(cls, value: str) -> str:
        return value.strip().upper()


class HoldingUpdateRequest(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=20)
    exchange: str | None = Field(default=None, min_length=1, max_length=20)
    quantity: float | None = Field(default=None, ge=0)
    average_cost: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("symbol", "exchange", "currency")
    @classmethod
    def normalize_optional_uppercase(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class HoldingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    symbol: str
    exchange: str
    quantity: float
    average_cost: float
    currency: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class TransactionCreateRequest(BaseModel):
    holding_id: str = Field(min_length=1)
    side: TransactionSide
    trade_date: date
    quantity: float = Field(gt=0)
    price: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    fees: float = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()


class TransactionUpdateRequest(BaseModel):
    side: TransactionSide | None = None
    trade_date: date | None = None
    quantity: float | None = Field(default=None, gt=0)
    price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    fees: float | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("currency")
    @classmethod
    def normalize_optional_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
