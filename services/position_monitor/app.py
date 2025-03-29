"""
Mock Position Monitor Service - Part of the BluefinAI Agent Trader Demo
Monitors active positions and triggers chart analysis at appropriate intervals
"""
import os
import time
import logging
import requests
import json
import random
from datetime import datetime, timedelta
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/position_monitor.log")
    ]
)
logger = logging.getLogger("position-monitor")

# Configuration
TRADING_SERVICE_URL = os.environ.get("TRADING_SERVICE_URL", "http://trading-service:5000")
CHART_SERVICE_URL = os.environ.get("CHART_SERVICE_URL", "http://chart-service:3333/capture")
AI_ANALYSIS_URL = os.environ.get("AI_ANALYSIS_URL", "http://ai-analysis:5000/analyze")

# Default settings
DEFAULT_SYMBOL = os.environ.get("DEFAULT_SYMBOL", "BTC/USD")
DEFAULT_TIMEFRAME = os.environ.get("DEFAULT_TIMEFRAME", "1h")
MONITORING_INTERVAL = int(os.environ.get("MONITORING_INTERVAL", 60))  # seconds
TIMEFRAMES = {
    "5m": 5 * 60,
    "15m": 15 * 60,
    "1h": 60 * 60,
    "4h": 4 * 60 * 60
}

class PositionMonitor:
    """Mock position monitoring service."""
    
    def __init__(self):
        self.running = False
        self.positions = {}
        self.last_update = datetime.now()
        self.monitor_thread = None
    
    def start(self):
        """Start the position monitoring service."""
        if self.running:
            logger.warning("Position monitor already running")
            return
        
        logger.info("Starting position monitor service")
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        """Stop the position monitoring service."""
        logger.info("Stopping position monitor service")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_positions()
                time.sleep(MONITORING_INTERVAL)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(MONITORING_INTERVAL)
    
    def _check_positions(self):
        """Check all active positions and update status."""
        logger.info("Checking active positions")
        
        try:
            # Fetch positions from trading service
            response = requests.get(f"{TRADING_SERVICE_URL}/api/positions")
            data = response.json()
            
            if data["status"] == "success":
                self.positions = data["data"]
                logger.info(f"Found {len(self.positions)} positions")
                
                # Process each active position
                for position_id, position in self.positions.items():
                    if position["status"] == "open":
                        self._monitor_position(position_id, position)
            else:
                logger.error(f"Error fetching positions: {data}")
        
        except Exception as e:
            logger.error(f"Error checking positions: {e}")
    
    def _monitor_position(self, position_id, position):
        """Monitor a specific position and decide if it needs analysis."""
        symbol = position["symbol"]
        
        # Determine if we need to analyze based on timeframe
        timeframe = DEFAULT_TIMEFRAME
        interval_seconds = TIMEFRAMES.get(timeframe, 3600)  # Default to 1h
        
        # Use timeframe ÷ 4 formula for monitoring frequency
        monitor_interval = interval_seconds / 4
        
        # Check if enough time has passed since last check
        time_since_last = (datetime.now() - self.last_update).total_seconds()
        
        if time_since_last >= monitor_interval:
            logger.info(f"Analyzing position {position_id} for {symbol}")
            self._trigger_analysis(position_id, position)
            self.last_update = datetime.now()
    
    def _trigger_analysis(self, position_id, position):
        """Trigger AI analysis for a position."""
        symbol = position["symbol"]
        
        try:
            # 1. Capture chart
            logger.info(f"Requesting chart for {symbol}")
            
            # 2. Analyze chart
            logger.info(f"Analyzing chart for {symbol}")
            response = requests.post(
                AI_ANALYSIS_URL,
                json={
                    "symbol": symbol,
                    "timeframe": DEFAULT_TIMEFRAME,
                    "position_id": position_id
                }
            )
            
            analysis = response.json()
            
            if analysis["status"] == "success":
                self._process_analysis(position_id, position, analysis["data"])
            else:
                logger.error(f"Analysis error: {analysis}")
        
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
    
    def _process_analysis(self, position_id, position, analysis):
        """Process the analysis result and take appropriate action."""
        logger.info(f"Processing analysis for position {position_id}")
        
        action = analysis["recommended_action"]
        confidence = analysis["confidence"]
        
        # Mock minimum confidence threshold
        min_confidence = 0.7
        
        if confidence < min_confidence:
            logger.info(f"Confidence too low ({confidence}), no action taken")
            return
        
        position_type = position["type"]
        
        try:
            # Determine if we need to close the position
            if (position_type == "long" and action == "CLOSE LONG") or \
               (position_type == "short" and action == "CLOSE SHORT"):
                
                logger.info(f"Closing {position_type} position {position_id} based on analysis")
                response = requests.post(
                    f"{TRADING_SERVICE_URL}/api/positions/close/{position_id}",
                    json={}
                )
                
                if response.json()["status"] == "success":
                    logger.info(f"Successfully closed position {position_id}")
                else:
                    logger.error(f"Error closing position: {response.json()}")
            else:
                logger.info(f"No action needed for {position_type} position based on {action}")
        
        except Exception as e:
            logger.error(f"Error processing analysis: {e}")

# Main entry point
if __name__ == "__main__":
    # Create and start the position monitor
    monitor = PositionMonitor()
    
    try:
        monitor.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected, shutting down")
    finally:
        monitor.stop() 