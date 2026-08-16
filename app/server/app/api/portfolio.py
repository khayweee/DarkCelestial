from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api_contracts.portfolio import (
    HoldingCreateRequest,
    HoldingResponse,
    HoldingUpdateRequest,
    TransactionCreateRequest,
    TransactionResponse,
    TransactionUpdateRequest,
)
from app.dependencies import get_portfolio_service
from app.domain.models import HoldingHasTransactionsError, HoldingNotFoundError, OversellError
from app.service.portfolio_service import PortfolioService

router = APIRouter(prefix="/users/{user_id}/portfolio", tags=["portfolio"])


@router.post("/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(
    user_id: str,
    payload: HoldingCreateRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingResponse:
    holding = await portfolio_service.create_holding(
        owner_id=user_id,
        symbol=payload.symbol,
        exchange=payload.exchange,
        quantity=payload.quantity,
        average_cost=payload.average_cost,
        currency=payload.currency,
        notes=payload.notes,
    )
    return HoldingResponse.model_validate(holding)


@router.get("/holdings", response_model=list[HoldingResponse])
async def list_holdings(
    user_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> list[HoldingResponse]:
    holdings = await portfolio_service.list_holdings(owner_id=user_id)
    return [HoldingResponse.model_validate(holding) for holding in holdings]


@router.get("/holdings/{holding_id}", response_model=HoldingResponse)
async def get_holding(
    user_id: str,
    holding_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingResponse:
    holding = await portfolio_service.get_holding(owner_id=user_id, holding_id=holding_id)
    if holding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")
    return HoldingResponse.model_validate(holding)


@router.patch("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    user_id: str,
    holding_id: str,
    payload: HoldingUpdateRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> HoldingResponse:
    holding = await portfolio_service.update_holding(
        owner_id=user_id,
        holding_id=holding_id,
        symbol=payload.symbol,
        exchange=payload.exchange,
        quantity=payload.quantity,
        average_cost=payload.average_cost,
        currency=payload.currency,
        notes=payload.notes,
    )
    if holding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")
    return HoldingResponse.model_validate(holding)


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    user_id: str,
    holding_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> Response:
    try:
        deleted = await portfolio_service.delete_holding(owner_id=user_id, holding_id=holding_id)
    except HoldingHasTransactionsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holding not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    user_id: str,
    payload: TransactionCreateRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> TransactionResponse:
    try:
        transaction = await portfolio_service.create_transaction(
            owner_id=user_id,
            holding_id=payload.holding_id,
            side=payload.side,
            trade_date=payload.trade_date,
            quantity=payload.quantity,
            price=payload.price,
            currency=payload.currency,
            fees=payload.fees,
            notes=payload.notes,
        )
    except HoldingNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OversellError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TransactionResponse.model_validate(transaction)


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    user_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> list[TransactionResponse]:
    transactions = await portfolio_service.list_transactions(owner_id=user_id)
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    user_id: str,
    transaction_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> TransactionResponse:
    transaction = await portfolio_service.get_transaction(owner_id=user_id, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionResponse.model_validate(transaction)


@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    user_id: str,
    transaction_id: str,
    payload: TransactionUpdateRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> TransactionResponse:
    try:
        transaction = await portfolio_service.update_transaction(
            owner_id=user_id,
            transaction_id=transaction_id,
            side=payload.side,
            trade_date=payload.trade_date,
            quantity=payload.quantity,
            price=payload.price,
            currency=payload.currency,
            fees=payload.fees,
            notes=payload.notes,
        )
    except OversellError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionResponse.model_validate(transaction)


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    user_id: str,
    transaction_id: str,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> Response:
    deleted = await portfolio_service.delete_transaction(owner_id=user_id, transaction_id=transaction_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
