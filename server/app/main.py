from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from app.api.websocket import router as websocket_router
from app.services.market_data import MarketDataStream
from app.services.connection_manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trading Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)

async def broadcast_market_data():
    stream = MarketDataStream()
    await stream.connect()
    try:
        async for data in stream.start_stream():
            await manager.broadcast(data)
    finally:
        await stream.disconnect()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting market data broadcast...")
    asyncio.create_task(broadcast_market_data())

@app.get("/health")
def health_check():
    return {"status": "ok"}
