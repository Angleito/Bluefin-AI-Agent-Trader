"""
Mock Trading Service - Part of the BluefinAI Agent Trader Demo
"""
from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/trading_service.log")
    ]
)
logger = logging.getLogger("trading-service")

# Initialize Flask app
app = Flask(__name__)

# Mock database
mock_positions = {}
mock_orders = {}
mock_market_data = {
    "BTC/USD": {
        "price": 65000.00,
        "24h_change": 2.5,
        "24h_volume": 1500000000
    },
    "ETH/USD": {
        "price": 3500.00,
        "24h_change": 1.8,
        "24h_volume": 850000000
    }
}

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/api/market_data", methods=["GET"])
def get_market_data():
    """Return mock market data."""
    symbol = request.args.get("symbol", "BTC/USD")
    if symbol in mock_market_data:
        return jsonify({
            "status": "success",
            "data": mock_market_data[symbol]
        })
    return jsonify({
        "status": "error",
        "message": f"Symbol {symbol} not found"
    }), 404

@app.route("/api/positions", methods=["GET"])
def get_positions():
    """Return all mock positions."""
    return jsonify({
        "status": "success",
        "data": mock_positions
    })

@app.route("/api/positions/open", methods=["POST"])
def open_position():
    """Mock opening a new position."""
    data = request.json
    position_id = f"pos_{len(mock_positions) + 1}"
    
    # Extract position details from request
    symbol = data.get("symbol", "BTC/USD")
    position_type = data.get("type", "long")
    size = data.get("size", 0.1)
    
    # Create mock position
    mock_positions[position_id] = {
        "id": position_id,
        "symbol": symbol,
        "type": position_type,
        "size": size,
        "entry_price": mock_market_data.get(symbol, {}).get("price", 50000),
        "status": "open",
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Created new position: {position_id}")
    return jsonify({
        "status": "success",
        "message": "Position opened",
        "data": mock_positions[position_id]
    })

@app.route("/api/positions/close/<position_id>", methods=["POST"])
def close_position(position_id):
    """Mock closing an existing position."""
    if position_id not in mock_positions:
        return jsonify({
            "status": "error",
            "message": f"Position {position_id} not found"
        }), 404
    
    # Close the position
    mock_positions[position_id]["status"] = "closed"
    mock_positions[position_id]["close_timestamp"] = datetime.now().isoformat()
    mock_positions[position_id]["exit_price"] = mock_market_data.get(
        mock_positions[position_id]["symbol"], {}).get("price", 50000)
    
    logger.info(f"Closed position: {position_id}")
    return jsonify({
        "status": "success",
        "message": "Position closed",
        "data": mock_positions[position_id]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 