"""
Strategy Service - Orchestrates trading strategies and execution

This module provides a service for orchestrating trading strategies and execution.
It combines AI signal generation with trade execution on Bluefin.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..config.config import config
from .bluefin_service import BluefinService
from .ai_agent_service import AIAgentService

class StrategyService:
    """
    Service for orchestrating trading strategies and execution.
    Combines AI signal generation with trade execution on Bluefin.
    """

    def __init__(self):
        """
        Initialize Strategy Service with configuration and dependencies.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load configuration
        self.trading_symbol = config.get('trading_parameters.trading_symbol', 'BTCUSDT')
        self.trading_interval = config.get('trading_parameters.trading_interval', '1h')
        self.leverage = int(config.get('trading_parameters.leverage', 10))
        self.order_type = config.get('trading_parameters.order_type', 'market')
        self.trade_amount_percentage = float(config.get('trading_parameters.trade_amount_percentage', 5))
        self.max_open_positions = int(config.get('trading_parameters.max_open_positions', 3))
        
        # Risk parameters
        self.risk_max_loss_percentage = float(config.get('risk_parameters.risk_max_loss_percentage', 2.0))
        self.stop_loss_percentage = float(config.get('risk_parameters.stop_loss_percentage', 1.5))
        self.take_profit_percentage = float(config.get('risk_parameters.take_profit_percentage', 3.0))
        self.trailing_stop_loss = config.get('risk_parameters.trailing_stop_loss', True)
        
        # Initialize services
        self.bluefin_service = BluefinService()
        self.ai_agent_service = AIAgentService()
        
        # Trading state
        self.active_positions = []
        self.last_signals = {}
        self.trading_enabled = False
        
        # Performance metrics
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'win_rate': 0.0,
            'average_profit': 0.0,
            'average_loss': 0.0,
            'largest_profit': 0.0,
            'largest_loss': 0.0
        }

    async def initialize(self) -> None:
        """
        Initialize the strategy service and its dependencies.
        """
        self.logger.info("Initializing Strategy Service")
        
        # Initialize Bluefin service
        await self.bluefin_service.initialize()
        
        # Load active positions
        await self.update_positions()
        
        # Enable trading
        self.trading_enabled = True
        
        self.logger.info("Strategy Service initialized successfully")

    async def update_positions(self) -> None:
        """
        Update active positions from Bluefin exchange.
        """
        self.active_positions = await self.bluefin_service.get_positions()
        self.logger.info(f"Updated positions: {len(self.active_positions)} active positions")

    async def execute_trading_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete trading cycle:
        1. Generate trading signal
        2. Validate signal against risk parameters
        3. Execute trade if signal is valid
        
        :param market_data: Market data for analysis
        :return: Trading cycle result
        """
        if not self.trading_enabled:
            return {'status': 'disabled', 'message': 'Trading is disabled'}
        
        # Update positions
        await self.update_positions()
        
        # Check if we can open new positions
        if len(self.active_positions) >= self.max_open_positions:
            return {
                'status': 'skipped',
                'message': f'Maximum open positions reached ({self.max_open_positions})'
            }
        
        # Generate trading signal
        signal = await self.ai_agent_service.generate_trading_signal(market_data)
        
        # Store last signal
        self.last_signals[market_data.get('symbol', 'unknown')] = signal
        
        # Validate signal
        if not self._validate_signal(signal):
            return {
                'status': 'rejected',
                'message': 'Signal validation failed',
                'signal': signal
            }
        
        # Check if signal is actionable
        if signal.get('signal') == 'hold':
            return {
                'status': 'hold',
                'message': 'Signal indicates to hold',
                'signal': signal
            }
        
        # Execute trade
        try:
            trade_result = await self._execute_trade(signal)
            return {
                'status': 'executed',
                'message': 'Trade executed successfully',
                'signal': signal,
                'trade': trade_result
            }
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return {
                'status': 'error',
                'message': f'Trade execution failed: {str(e)}',
                'signal': signal
            }

    def _validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate a trading signal against risk parameters.
        
        :param signal: Trading signal to validate
        :return: True if signal is valid, False otherwise
        """
        # Check if signal is present
        if 'signal' not in signal:
            self.logger.warning("Signal validation failed: No signal type")
            return False
        
        # Check if confidence is high enough
        confidence = signal.get('confidence', 0)
        min_confidence = config.get('ai_agent_parameters.decision_confidence_threshold', 0.8)
        if confidence < min_confidence:
            self.logger.info(f"Signal validation failed: Confidence too low ({confidence} < {min_confidence})")
            return False
        
        # Check if we have stop loss and take profit for non-hold signals
        if signal['signal'] != 'hold' and ('stop_loss' not in signal or 'take_profit' not in signal):
            self.logger.warning("Signal validation failed: Missing stop loss or take profit")
            return False
        
        return True

    async def _execute_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade based on a trading signal.
        
        :param signal: Trading signal to execute
        :return: Trade execution result
        """
        # Get account balance
        account = await self.bluefin_service.get_account_balance()
        available_balance = account.get('available_balance', 0)
        
        # Calculate trade size
        trade_amount = available_balance * (self.trade_amount_percentage / 100)
        symbol = signal.get('symbol', self.trading_symbol)
        price = signal.get('price', 0)
        
        if price <= 0:
            # Get current market price
            market_data = await self.bluefin_service.get_market_data(symbol)
            price = market_data.get('price', 0)
        
        if price <= 0:
            raise ValueError("Invalid price for trade execution")
        
        # Calculate size in base currency
        size = trade_amount / price
        
        # Prepare order data
        order_data = {
            'symbol': symbol,
            'side': signal.get('signal'),  # 'buy' or 'sell'
            'type': self.order_type,
            'size': size,
            'leverage': self.leverage
        }
        
        # Add stop loss and take profit
        if 'stop_loss' in signal:
            order_data['stop_loss'] = signal['stop_loss']
        elif signal.get('signal') == 'buy':
            order_data['stop_loss'] = price * (1 - self.stop_loss_percentage / 100)
        elif signal.get('signal') == 'sell':
            order_data['stop_loss'] = price * (1 + self.stop_loss_percentage / 100)
        
        if 'take_profit' in signal:
            order_data['take_profit'] = signal['take_profit']
        elif signal.get('signal') == 'buy':
            order_data['take_profit'] = price * (1 + self.take_profit_percentage / 100)
        elif signal.get('signal') == 'sell':
            order_data['take_profit'] = price * (1 - self.take_profit_percentage / 100)
        
        # Execute order
        order_result = await self.bluefin_service.place_order(order_data)
        
        # Update performance metrics
        self.performance_metrics['total_trades'] += 1
        
        # Log trade
        self.logger.info(f"Trade executed: {signal.get('signal')} {size} {symbol} at {price}")
        
        return order_result

    async def update_profit_loss(self) -> Dict[str, float]:
        """
        Update profit and loss for active positions.
        
        :return: Dictionary with total unrealized P&L
        """
        # Update positions
        await self.update_positions()
        
        # Calculate total P&L
        total_pnl = sum(position.get('unrealized_pnl', 0) for position in self.active_positions)
        
        return {
            'total_unrealized_pnl': total_pnl,
            'positions_count': len(self.active_positions)
        }

    async def close_all_positions(self) -> List[Dict[str, Any]]:
        """
        Close all active positions.
        
        :return: List of position closure results
        """
        # Update positions
        await self.update_positions()
        
        # Close each position
        results = []
        for position in self.active_positions:
            try:
                result = await self.bluefin_service.close_position(position['id'])
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to close position {position['id']}: {e}")
                results.append({
                    'position_id': position['id'],
                    'status': 'error',
                    'error': str(e)
                })
        
        # Update positions again
        await self.update_positions()
        
        return results

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the strategy.
        
        :return: Performance metrics
        """
        # Calculate derived metrics
        total_trades = self.performance_metrics['total_trades']
        if total_trades > 0:
            self.performance_metrics['win_rate'] = (self.performance_metrics['winning_trades'] / total_trades) * 100
        
        winning_trades = self.performance_metrics['winning_trades']
        if winning_trades > 0:
            self.performance_metrics['average_profit'] = self.performance_metrics['total_profit'] / winning_trades
        
        losing_trades = self.performance_metrics['losing_trades']
        if losing_trades > 0:
            self.performance_metrics['average_loss'] = self.performance_metrics['total_loss'] / losing_trades
        
        return self.performance_metrics

    def enable_trading(self, enabled: bool = True) -> None:
        """
        Enable or disable trading.
        
        :param enabled: True to enable trading, False to disable
        """
        self.trading_enabled = enabled
        self.logger.info(f"Trading {'enabled' if enabled else 'disabled'}")

    async def start_websocket_listeners(self) -> None:
        """
        Start WebSocket listeners for real-time market data.
        In the template, this is a placeholder.
        """
        self.logger.info("WebSocket listeners not implemented in template")
        # In a real implementation, you would start WebSocket listeners here
