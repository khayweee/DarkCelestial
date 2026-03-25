import asyncio
import json
import websockets
from app.services.analysis import TechnicalAnalyzer
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

class MarketDataStream:
    def __init__(self):
        # We will connect to Binance for crypto, but yfinance logic could be easily added here
        # for NYSE simulation by pulling 1m bars in a separate thread.
        self.binance_url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
        self.analyzer = TechnicalAnalyzer()
        self.ws = None
        self._connected = False

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.binance_url)
            self._connected = True
            logger.info("Connected to Binance WebSocket (Crypto)")
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")

    async def disconnect(self):
        self._connected = False
        if self.ws:
            await self.ws.close()

    async def start_stream(self):
        if not self.ws:
            return
            
        try:
            async for message in self.ws:
                if not self._connected:
                    break
                data = json.loads(message)
                price = float(data['p'])
                
                # Analyze tick data
                self.analyzer.add_price(price)
                analysis = self.analyzer.compute_indicators()
                
                yield analysis
        except Exception as e:
            logger.error(f"WebSocket execution error: {e}")
