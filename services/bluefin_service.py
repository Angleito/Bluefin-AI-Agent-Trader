import os
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional, List, Union
from bluefin_v2_client import BluefinClient, Networks, Exchanges

class BluefinService:
    """
    Service for handling interactions with the Bluefin exchange API.
    Manages authentication, order placement, position tracking, and WebSocket connections.
    Aligned with the latest Bluefin Protocol integration guidelines.
    """

    def __init__(self, 
                 network: Optional[str] = None, 
                 private_key: Optional[str] = None,
                 exchange: str = Exchanges.BLUEFIN):
        """
        Initialize BluefinService with network, authentication, and exchange details.
        
        :param network: Bluefin network (SUI_PROD/SUI_STAGING), defaults to environment variable
        :param private_key: Private key for wallet, defaults to environment variable
        :param exchange: Specific exchange to interact with (default: BLUEFIN)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Network configuration
        self.network = network or os.getenv('BLUEFIN_NETWORK', 'SUI_STAGING')
        self.private_key = private_key or os.getenv('BLUEFIN_PRIVATE_KEY')
        self.exchange = exchange
        
        # Client and API configuration
        self.client = None
        self.api_url = os.getenv('BLUEFIN_API_URL', 'https://api.bluefin.io')
        
        # Enhanced retry and error handling
        self.max_retries = int(os.getenv('BLUEFIN_MAX_RETRIES', 3))
        self.retry_delay = float(os.getenv('BLUEFIN_RETRY_DELAY', 1.0))
        
        # Logging configuration
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def initialize(self) -> None:
        """
        Initialize Bluefin client with comprehensive authentication and network configuration.
        Supports multiple exchanges and enhanced error handling.
        """
        try:
            if not self.private_key:
                raise ValueError("Bluefin private key is required for initialization")
            
            self.client = BluefinClient(
                agree_to_terms=True,
                network=Networks[self.network],
                private_key=self.private_key,
                exchange=self.exchange
            )
            
            await self.client.init(validate_on_chain=True)
            self.logger.info(f"Bluefin client initialized on {self.network} for {self.exchange}")
        
        except Exception as e:
            self.logger.error(f"Comprehensive Bluefin client initialization failed: {e}")
            raise RuntimeError(f"Client initialization error: {e}")

    async def place_order(self, 
                           symbol: str, 
                           side: str, 
                           quantity: float, 
                           order_type: str = "MARKET", 
                           price: Optional[float] = None,
                           leverage: Optional[float] = None) -> Dict[str, Any]:
        """
        Enhanced order placement with comprehensive error handling and configuration.
        
        :param symbol: Trading pair symbol
        :param side: Order side (BUY/SELL)
        :param quantity: Order quantity
        :param order_type: Order type (MARKET/LIMIT)
        :param price: Price for limit orders
        :param leverage: Optional leverage for the order
        :return: Detailed order response
        """
        for attempt in range(self.max_retries):
            try:
                order_params = {
                    "symbol": symbol,
                    "side": side.upper(),
                    "quantity": quantity,
                    "order_type": order_type.upper()
                }
                
                if price and order_type.upper() == "LIMIT":
                    order_params["price"] = price
                
                if leverage is not None:
                    order_params["leverage"] = leverage
                
                order_response = await self.client.place_order(**order_params)
                
                self.logger.info(f"Order placed successfully: {order_response}")
                return order_response
            
            except Exception as e:
                self.logger.warning(f"Order placement failed (Attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to place order after {self.max_retries} attempts: {e}")
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def cancel_order(self, 
                            symbol: str, 
                            order_id: Optional[str] = None, 
                            all_orders: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Advanced order cancellation supporting single and multiple order cancellations.
        
        :param symbol: Trading pair symbol
        :param order_id: Specific order ID to cancel
        :param all_orders: Flag to cancel all orders for the symbol
        :return: Cancellation response
        """
        try:
            if all_orders:
                return await self.client.cancel_all_orders(symbol)
            
            if order_id:
                return await self.client.cancel_order(symbol, order_id)
            
            raise ValueError("Must specify either order_id or set all_orders to True")
        
        except Exception as e:
            self.logger.error(f"Order cancellation failed: {e}")
            raise RuntimeError(f"Cancellation error: {e}")

    async def get_positions(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Retrieve comprehensive position information.
        
        :param symbol: Optional specific symbol to retrieve position for
        :return: Detailed positions data
        """
        try:
            return await self.client.get_positions(symbol) if symbol else await self.client.get_positions()
        except Exception as e:
            self.logger.error(f"Failed to retrieve positions: {e}")
            raise RuntimeError(f"Position retrieval error: {e}")

    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Retrieve detailed account balance information.
        
        :return: Comprehensive account balance details
        """
        try:
            return await self.client.get_account_balance()
        except Exception as e:
            self.logger.error(f"Failed to retrieve account balance: {e}")
            raise RuntimeError(f"Account balance retrieval error: {e}")

    async def setup_websocket(self, 
                               order_callback=None, 
                               position_callback=None, 
                               trade_callback=None):
        """
        Advanced WebSocket setup with multiple event handlers.
        
        :param order_callback: Callback for order updates
        :param position_callback: Callback for position updates
        :param trade_callback: Callback for trade updates
        """
        try:
            await self.client.socket.open()
            
            # Subscribe to comprehensive user updates
            await self.client.socket.subscribe_user_update_by_token()
            
            # Register multiple event handlers
            if order_callback:
                @self.client.socket.on("order_update")
                async def on_order_update(data):
                    await order_callback(data)
            
            if position_callback:
                @self.client.socket.on("position_update")
                async def on_position_update(data):
                    await position_callback(data)
            
            if trade_callback:
                @self.client.socket.on("trade_update")
                async def on_trade_update(data):
                    await trade_callback(data)
            
            self.logger.info("Comprehensive WebSocket connection established")
        
        except Exception as e:
            self.logger.error(f"Advanced WebSocket setup failed: {e}")
            raise RuntimeError(f"WebSocket initialization error: {e}")