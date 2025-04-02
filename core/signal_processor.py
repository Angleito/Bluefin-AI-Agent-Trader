import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from config.config import TRADING_PARAMS, RISK_PARAMS

# Signal type constants
BULLISH_SIGNALS = ["GREEN_CIRCLE", "GOLD_CIRCLE", "BULL_FLAG"]
BEARISH_SIGNALS = ["RED_CIRCLE", "BEAR_FLAG", "BEAR_DIAMOND"]

class SignalProcessor:
    def __init__(self):
        """
        Initialize the SignalProcessor with logging and configuration
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.allowed_pairs = TRADING_PARAMS.get('allowed_trading_pairs', [])

    def process_tradingview_alert(self, alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process TradingView webhook alert and convert to trade recommendation
        
        :param alert_data: Dictionary containing alert information
        :return: Processed trade recommendation or None if invalid
        """
        # Validate required fields
        required = ["symbol", "timeframe", "signal_type"]
        if not all(field in alert_data for field in required):
            self.logger.warning(f"Invalid alert data: missing required fields {required}")
            return None
        
        # Validate symbol
        symbol = self.map_tradingview_to_bluefin_symbol(alert_data["symbol"])
        if symbol not in self.allowed_pairs:
            self.logger.warning(f"Symbol {symbol} not in allowed trading pairs")
            return None
        
        # Determine trade direction
        direction = self.get_trade_direction(
            alert_data["signal_type"],
            alert_data.get("action")
        )
        
        return {
            "symbol": symbol,
            "type": direction,
            "timeframe": alert_data["timeframe"],
            "entry_time": datetime.utcnow().isoformat(),
            "position_size": self.calculate_position_size(),
            "leverage": TRADING_PARAMS.get("leverage", 5),
            "stop_loss": self.calculate_stop_loss(direction),
            "confidence": self.calculate_signal_confidence(alert_data["signal_type"])
        }

    def map_tradingview_to_bluefin_symbol(self, tv_symbol: str) -> str:
        """
        Convert TradingView symbol to Bluefin symbol format
        
        :param tv_symbol: TradingView symbol
        :return: Bluefin-compatible symbol
        """
        if "/" in tv_symbol:  # SUI/USD -> SUI-PERP
            return f"{tv_symbol.split('/')[0]}-PERP"
        return f"{tv_symbol}-PERP"

    def get_trade_direction(self, signal_type: str, action: Optional[str] = None) -> str:
        """
        Determine trade direction based on signal type
        
        :param signal_type: Type of trading signal
        :param action: Optional action parameter
        :return: Trade direction ('LONG' or 'SHORT')
        """
        if signal_type in BULLISH_SIGNALS:
            return "LONG"
        elif signal_type in BEARISH_SIGNALS:
            return "SHORT"
        
        self.logger.warning(f"Unrecognized signal type: {signal_type}")
        return "NEUTRAL"

    def calculate_position_size(self) -> float:
        """
        Calculate position size based on trading parameters
        
        :return: Position size percentage
        """
        return TRADING_PARAMS.get(
            "position_size_percentage", 
            0.05  # Default 5%
        )

    def calculate_stop_loss(self, direction: str) -> Optional[float]:
        """
        Calculate stop loss based on trading direction and risk parameters
        
        :param direction: Trade direction
        :return: Stop loss value or None
        """
        # Placeholder implementation - would typically involve more complex calculation
        risk_percentage = RISK_PARAMS.get('max_loss_percentage', 0.02)
        return risk_percentage

    def calculate_signal_confidence(self, signal_type: str) -> float:
        """
        Calculate confidence score for a given signal type
        
        :param signal_type: Type of trading signal
        :return: Confidence score (0-1)
        """
        if signal_type in BULLISH_SIGNALS + BEARISH_SIGNALS:
            return 0.7  # Base confidence
        
        # Additional confidence scoring logic can be added here
        return 0.5  # Neutral confidence for unrecognized signals