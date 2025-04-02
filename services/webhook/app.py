"""
Mock Webhook Service - Part of the BluefinAI Agent Trader Demo
Handles incoming trading signals from external sources
"""
from flask import Flask, request, jsonify
import os
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/webhook_service.log")
    ]
)
logger = logging.getLogger("webhook-service")

# Initialize Flask app
app = Flask(__name__)

# Configuration
TRADING_SERVICE_URL = os.environ.get("TRADING_SERVICE_URL", "http://trading-service:5000")

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    """Receive and process webhook from TradingView or other sources."""
    data = request.json
    
    if not data:
        return jsonify({
            "status": "error",
            "message": "No data received"
        }), 400
    
    logger.info(f"Received webhook: {json.dumps(data)}")
    
    # Extract signal details
    symbol = data.get("symbol", "BTC/USD")
    action = data.get("action", "").upper()
    
    # Validate required fields
    if not action:
        return jsonify({
            "status": "error",
            "message": "No action specified"
        }), 400
    
    # Process the action
    if "LONG" in action:
        if "OPEN" in action:
            return open_long_position(symbol, data)
        elif "CLOSE" in action:
            return close_long_position(symbol, data)
    elif "SHORT" in action:
        if "OPEN" in action:
            return open_short_position(symbol, data)
        elif "CLOSE" in action:
            return close_short_position(symbol, data)
    
    return jsonify({
        "status": "error",
        "message": f"Unknown action: {action}"
    }), 400

def open_long_position(symbol, data):
    """Open a long position via the trading service."""
    try:
        response = requests.post(
            f"{TRADING_SERVICE_URL}/api/positions/open",
            json={
                "symbol": symbol,
                "type": "long",
                "size": data.get("size", 0.1)
            }
        )
        logger.info(f"Open long response: {response.text}")
        return jsonify({
            "status": "success",
            "message": "Long position opened",
            "data": response.json()
        })
    except Exception as e:
        logger.error(f"Error opening long position: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error opening position: {str(e)}"
        }), 500

def close_long_position(symbol, data):
    """Close a long position via the trading service."""
    # In a real system, we would need to find the position ID
    # For this mock, we'll just assume position ID 1
    position_id = data.get("position_id", "pos_1")
    try:
        response = requests.post(
            f"{TRADING_SERVICE_URL}/api/positions/close/{position_id}",
            json={}
        )
        logger.info(f"Close long response: {response.text}")
        return jsonify({
            "status": "success",
            "message": "Long position closed",
            "data": response.json()
        })
    except Exception as e:
        logger.error(f"Error closing long position: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error closing position: {str(e)}"
        }), 500

def open_short_position(symbol, data):
    """Open a short position via the trading service."""
    try:
        response = requests.post(
            f"{TRADING_SERVICE_URL}/api/positions/open",
            json={
                "symbol": symbol,
                "type": "short",
                "size": data.get("size", 0.1)
            }
        )
        logger.info(f"Open short response: {response.text}")
        return jsonify({
            "status": "success",
            "message": "Short position opened",
            "data": response.json()
        })
    except Exception as e:
        logger.error(f"Error opening short position: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error opening position: {str(e)}"
        }), 500

def close_short_position(symbol, data):
    """Close a short position via the trading service."""
    # In a real system, we would need to find the position ID
    # For this mock, we'll just assume position ID 1
    position_id = data.get("position_id", "pos_1")
    try:
        response = requests.post(
            f"{TRADING_SERVICE_URL}/api/positions/close/{position_id}",
            json={}
        )
        logger.info(f"Close short response: {response.text}")
        return jsonify({
            "status": "success",
            "message": "Short position closed",
            "data": response.json()
        })
    except Exception as e:
        logger.error(f"Error closing short position: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error closing position: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port) 