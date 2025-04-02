import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from core.risk_manager import RiskManager
from services.bluefin_service import BluefinService
from core.trade_executor import TradeExecutor

class PositionService:
    """
    Position Service for tracking, monitoring, and managing trading positions.
    Handles real-time position tracking, risk assessment, and automated adjustments.
    """

    def __init__(self, 
                 bluefin_service: Optional[BluefinService] = None, 
                 risk_manager: Optional[RiskManager] = None,
                 check_interval: int = 60,
                 max_positions: int = 10):
        """
        Initialize Position Service with dependencies and configuration.
        
        :param bluefin_service: Bluefin exchange service for position interactions
        :param risk_manager: Risk management component
        :param check_interval: Interval between position health checks (seconds)
        :param max_positions: Maximum number of concurrent positions
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Dependencies
        self.bluefin_service = bluefin_service or BluefinService()
        self.risk_manager = risk_manager or RiskManager()
        self.trade_executor = TradeExecutor()
        
        # Configuration
        self.check_interval = check_interval
        self.max_positions = max_positions
        
        # Position tracking
        self.active_positions: List[Dict[str, Any]] = []
        self.position_history: List[Dict[str, Any]] = []
        
        # Monitoring flags
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False

    async def start_monitoring(self):
        """
        Start continuous position monitoring loop.
        Runs asynchronously to check and manage positions periodically.
        """
        if self._is_monitoring:
            self.logger.warning("Position monitoring is already running")
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Position monitoring started")

    async def _monitoring_loop(self):
        """
        Internal monitoring loop for continuous position health checks.
        """
        try:
            while self._is_monitoring:
                await self.check_positions()
                await asyncio.sleep(self.check_interval)
        except Exception as e:
            self.logger.error(f"Position monitoring loop error: {e}")
            self._is_monitoring = False
        finally:
            self.logger.info("Position monitoring loop stopped")

    async def stop_monitoring(self):
        """
        Stop the position monitoring loop.
        """
        if self._monitoring_task:
            self._is_monitoring = False
            await self._monitoring_task
            self._monitoring_task = None
            self.logger.info("Position monitoring stopped")

    async def check_positions(self):
        """
        Comprehensive check of all open positions.
        Performs risk assessment and potential position adjustments.
        """
        try:
            # Retrieve current positions from Bluefin
            current_positions = await self.bluefin_service.get_positions()
            
            for position in current_positions:
                # Assess position health and risk
                risk_assessment = self.risk_manager.assess_position_risk(position)
                
                # Determine if position needs adjustment
                if risk_assessment['needs_adjustment']:
                    await self.adjust_position(position, risk_assessment)
                
                # Update active positions list
                self._update_active_positions(position)
        
        except Exception as e:
            self.logger.error(f"Position checking failed: {e}")

    async def adjust_position(self, position: Dict[str, Any], risk_assessment: Dict[str, Any]):
        """
        Adjust a position based on risk assessment.
        
        :param position: Current position details
        :param risk_assessment: Risk assessment results
        """
        try:
            adjustment_type = risk_assessment.get('adjustment_type')
            
            if adjustment_type == 'partial_close':
                close_percentage = risk_assessment.get('close_percentage', 0.5)
                await self.trade_executor.partial_close_position(
                    position['symbol'], 
                    close_percentage
                )
                self.logger.info(f"Partially closed position: {position['symbol']}")
            
            elif adjustment_type == 'stop_loss':
                new_stop_loss = risk_assessment.get('stop_loss_price')
                await self.trade_executor.update_stop_loss(
                    position['symbol'], 
                    new_stop_loss
                )
                self.logger.info(f"Updated stop loss for {position['symbol']}")
            
            elif adjustment_type == 'liquidate':
                await self.trade_executor.close_position(position['symbol'])
                self.logger.warning(f"Liquidated high-risk position: {position['symbol']}")
        
        except Exception as e:
            self.logger.error(f"Position adjustment failed: {e}")

    def _update_active_positions(self, position: Dict[str, Any]):
        """
        Update the list of active positions and maintain position history.
        
        :param position: Position to update
        """
        # Remove existing position if it exists
        self.active_positions = [
            p for p in self.active_positions 
            if p['symbol'] != position['symbol']
        ]
        
        # Add current position
        self.active_positions.append(position)
        
        # Maintain position history
        self.position_history.append({
            **position,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history size
        if len(self.position_history) > 100:
            self.position_history = self.position_history[-100:]

    def get_position_performance(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve position performance metrics.
        
        :param symbol: Optional specific symbol to filter
        :return: List of position performance metrics
        """
        if symbol:
            return [
                pos for pos in self.position_history 
                if pos['symbol'] == symbol
            ]
        return self.position_history

    def get_active_positions(self) -> List[Dict[str, Any]]:
        """
        Get currently active trading positions.
        
        :return: List of active positions
        """
        return self.active_positions.copy()

    async def create_position(self, symbol: str, side: str, quantity: float, 
                               order_type: str = 'MARKET', price: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a new trading position.
        
        :param symbol: Trading pair symbol
        :param side: Trade side (BUY/SELL)
        :param quantity: Position size
        :param order_type: Order type (MARKET/LIMIT)
        :param price: Price for limit orders
        :return: Created position details
        """
        try:
            # Check position count limit
            if len(self.active_positions) >= self.max_positions:
                raise ValueError(f"Maximum positions ({self.max_positions}) reached")
            
            # Place order through trade executor
            position = await self.trade_executor.open_position(
                symbol, side, quantity, order_type, price
            )
            
            # Update active positions
            self._update_active_positions(position)
            
            self.logger.info(f"Created new position: {symbol} - {side}")
            return position
        
        except Exception as e:
            self.logger.error(f"Position creation failed: {e}")
            raise

    async def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close an existing position.
        
        :param symbol: Symbol of position to close
        :return: Closed position details
        """
        try:
            # Close position through trade executor
            closed_position = await self.trade_executor.close_position(symbol)
            
            # Remove from active positions
            self.active_positions = [
                p for p in self.active_positions 
                if p['symbol'] != symbol
            ]
            
            self.logger.info(f"Closed position: {symbol}")
            return closed_position
        
        except Exception as e:
            self.logger.error(f"Position closing failed: {e}")
            raise