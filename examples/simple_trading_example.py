"""
Simple Trading Example

This example demonstrates how to use the Bluefin AI Agent Trader template
to create a simple trading bot that runs in simulation mode.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the path so we can import from the template
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from services.bluefin_service import BluefinService
from services.ai_agent_service import AIAgentService
from services.strategy_service import StrategyService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run_simple_trading_example():
    """
    Run a simple trading example using the template.
    """
    logger.info("Starting simple trading example")
    
    # Initialize services
    bluefin_service = BluefinService()
    ai_agent_service = AIAgentService()
    strategy_service = StrategyService()
    
    # Initialize strategy service
    await strategy_service.initialize()
    
    # Trading parameters
    symbol = "BTCUSDT"
    trading_cycles = 10
    
    logger.info(f"Running {trading_cycles} trading cycles for {symbol}")
    
    # Get initial account balance
    account = await bluefin_service.get_account_balance()
    initial_balance = account.get('total_balance', 0)
    logger.info(f"Initial balance: {initial_balance:.2f}")
    
    # Run trading cycles
    for i in range(trading_cycles):
        logger.info(f"Trading cycle {i+1}/{trading_cycles}")
        
        # Get market data
        market_data = await bluefin_service.get_market_data(symbol)
        logger.info(f"Current price of {symbol}: {market_data.get('price', 0):.2f}")
        
        # Generate trading signal
        signal = await ai_agent_service.generate_trading_signal(market_data)
        logger.info(f"Signal: {signal.get('signal')} with confidence {signal.get('confidence', 0):.2f}")
        
        # Execute trading cycle
        result = await strategy_service.execute_trading_cycle(market_data)
        logger.info(f"Trading cycle result: {result['status']} - {result['message']}")
        
        # Update profit/loss
        pnl = await strategy_service.update_profit_loss()
        logger.info(f"Current P&L: {pnl['total_unrealized_pnl']:.2f} with {pnl['positions_count']} positions")
        
        # Wait a bit between cycles
        await asyncio.sleep(2)
    
    # Get final account balance
    account = await bluefin_service.get_account_balance()
    final_balance = account.get('total_balance', 0)
    logger.info(f"Final balance: {final_balance:.2f}")
    logger.info(f"Profit/Loss: {final_balance - initial_balance:.2f}")
    
    # Close all positions
    logger.info("Closing all positions")
    results = await strategy_service.close_all_positions()
    logger.info(f"Closed {len(results)} positions")
    
    # Get performance metrics
    metrics = strategy_service.get_performance_metrics()
    logger.info(f"Performance metrics: {metrics}")
    
    logger.info("Simple trading example completed")

if __name__ == "__main__":
    # Force simulation mode
    os.environ["SIMULATION_MODE"] = "true"
    
    # Run the example
    asyncio.run(run_simple_trading_example())
