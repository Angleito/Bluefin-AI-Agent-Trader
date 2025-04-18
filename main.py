"""
Bluefin AI Agent Trader - Main Application

This is the main entry point for the Bluefin AI Agent Trader application.
It initializes the services and starts the trading loop.
"""

import os
import sys
import json
import logging
import asyncio
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from config.config import config
from services.bluefin_service import BluefinService
from services.ai_agent_service import AIAgentService
from services.strategy_service import StrategyService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/trader.log')
    ]
)

logger = logging.getLogger(__name__)

# Global variables
strategy_service = None
shutdown_event = asyncio.Event()

async def initialize_services() -> StrategyService:
    """
    Initialize all services required for trading.
    
    :return: Initialized strategy service
    """
    logger.info("Initializing services...")
    
    # Create strategy service
    strategy = StrategyService()
    
    # Initialize strategy service
    await strategy.initialize()
    
    logger.info("Services initialized successfully")
    return strategy

async def trading_loop(strategy: StrategyService, interval_seconds: int = 60) -> None:
    """
    Main trading loop that executes trading cycles at regular intervals.
    
    :param strategy: Strategy service to use for trading
    :param interval_seconds: Interval between trading cycles in seconds
    """
    logger.info(f"Starting trading loop with {interval_seconds}s interval")
    
    # Trading symbols
    symbols = config.get('simulation_parameters.symbols', ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
    
    while not shutdown_event.is_set():
        try:
            for symbol in symbols:
                # Get market data
                market_data = await strategy.bluefin_service.get_market_data(symbol)
                
                # Execute trading cycle
                result = await strategy.execute_trading_cycle(market_data)
                
                # Log result
                logger.info(f"Trading cycle for {symbol}: {result['status']} - {result['message']}")
                
                # Update profit/loss
                pnl = await strategy.update_profit_loss()
                logger.info(f"Current P&L: {pnl['total_unrealized_pnl']:.2f} with {pnl['positions_count']} positions")
            
            # Wait for next cycle
            await asyncio.sleep(interval_seconds)
            
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            await asyncio.sleep(5)  # Short delay before retry

async def shutdown() -> None:
    """
    Gracefully shutdown the application.
    """
    logger.info("Shutting down...")
    
    # Signal the trading loop to stop
    shutdown_event.set()
    
    # Close all positions if strategy service is initialized
    if strategy_service:
        try:
            logger.info("Closing all positions...")
            results = await strategy_service.close_all_positions()
            logger.info(f"Closed {len(results)} positions")
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
    
    logger.info("Shutdown complete")

def handle_signals() -> None:
    """
    Set up signal handlers for graceful shutdown.
    """
    loop = asyncio.get_event_loop()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

async def main() -> None:
    """
    Main entry point for the application.
    """
    global strategy_service
    
    try:
        # Set up signal handlers
        handle_signals()
        
        # Print banner
        print("""
        ╔══════════════════════════════════════════════════════╗
        ║                                                      ║
        ║             BLUEFIN AI AGENT TRADER                  ║
        ║                                                      ║
        ║              TEMPLATE VERSION                        ║
        ║                                                      ║
        ╚══════════════════════════════════════════════════════╝
        """)
        
        # Log startup information
        logger.info("Starting Bluefin AI Agent Trader")
        logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        logger.info(f"Simulation mode: {config.is_simulation_mode()}")
        
        # Initialize services
        strategy_service = await initialize_services()
        
        # Start trading loop
        await trading_loop(strategy_service)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await shutdown()
        sys.exit(1)

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the main function
    asyncio.run(main())
