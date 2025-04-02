import logging
from typing import Dict, Any, Optional, Union

from services.bluefin_service import BluefinService
from config.config import TRADING_PARAMS

class TradeExecutor:
    def __init__(self, bluefin_service: Optional[BluefinService] = None):
        """
        Initialize TradeExecutor with Bluefin exchange interface
        
        :param bluefin_service: Optional Bluefin service for trade execution
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Use provided service or create a new one
        self.bluefin_service = bluefin_service or BluefinService()
        
        # Trading configuration
        self.max_order_attempts = TRADING_PARAMS.get('max_order_attempts', 3)
        self.order_timeout = TRADING_PARAMS.get('order_timeout', 30)  # seconds

    def place_market_order(self, trade_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a market order based on trade recommendation
        
        :param trade_recommendation: Processed trade signal
        :return: Order execution result
        """
        try:
            order_params = {
                'symbol': trade_recommendation['symbol'],
                'side': trade_recommendation['type'],
                'order_type': 'MARKET',
                'quantity': self._calculate_order_quantity(trade_recommendation),
                'leverage': trade_recommendation.get('leverage', 5)
            }
            
            # Execute order with retry mechanism
            for attempt in range(self.max_order_attempts):
                try:
                    order_result = self.bluefin_service.create_order(**order_params)
                    
                    self.logger.info(f"Market order placed: {order_result}")
                    return order_result
                
                except Exception as retry_error:
                    self.logger.warning(f"Order attempt {attempt + 1} failed: {retry_error}")
                    if attempt == self.max_order_attempts - 1:
                        raise
            
        except Exception as e:
            self.logger.error(f"Failed to place market order: {e}")
            raise

    def place_limit_order(self, trade_recommendation: Dict[str, Any], price: float) -> Dict[str, Any]:
        """
        Place a limit order at a specified price
        
        :param trade_recommendation: Processed trade signal
        :param price: Limit order price
        :return: Order execution result
        """
        try:
            order_params = {
                'symbol': trade_recommendation['symbol'],
                'side': trade_recommendation['type'],
                'order_type': 'LIMIT',
                'quantity': self._calculate_order_quantity(trade_recommendation),
                'price': price,
                'leverage': trade_recommendation.get('leverage', 5)
            }
            
            order_result = self.bluefin_service.create_order(**order_params)
            self.logger.info(f"Limit order placed: {order_result}")
            return order_result
        
        except Exception as e:
            self.logger.error(f"Failed to place limit order: {e}")
            raise

    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        :param order_id: Unique identifier for the order
        :param symbol: Trading symbol
        :return: Cancellation result
        """
        try:
            cancellation_result = self.bluefin_service.cancel_order(
                symbol=symbol, 
                order_id=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return cancellation_result
        
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            raise

    def modify_order(self, 
                     order_id: str, 
                     symbol: str, 
                     quantity: Optional[float] = None, 
                     price: Optional[float] = None) -> Dict[str, Any]:
        """
        Modify an existing order's quantity or price
        
        :param order_id: Unique identifier for the order
        :param symbol: Trading symbol
        :param quantity: New order quantity (optional)
        :param price: New order price (optional)
        :return: Order modification result
        """
        try:
            modification_result = self.bluefin_service.modify_order(
                symbol=symbol,
                order_id=order_id,
                quantity=quantity,
                price=price
            )
            
            self.logger.info(f"Order {order_id} modified successfully")
            return modification_result
        
        except Exception as e:
            self.logger.error(f"Failed to modify order {order_id}: {e}")
            raise

    def _calculate_order_quantity(self, trade_recommendation: Dict[str, Any]) -> float:
        """
        Calculate order quantity based on account balance and position size
        
        :param trade_recommendation: Trade signal with position size
        :return: Order quantity
        """
        account_balance = self.bluefin_service.get_account_balance()
        position_size_percentage = trade_recommendation.get('position_size', 0.05)
        
        order_quantity = account_balance * position_size_percentage
        
        return order_quantity