"""
Mock Chart Service - Part of the BluefinAI Agent Trader Demo
Handles chart captures and TradingView interactions
"""
from flask import Flask, request, jsonify, send_file
import os
import logging
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/chart_service.log")
    ]
)
logger = logging.getLogger("chart-service")

# Initialize Flask app
app = Flask(__name__)

# Ensure screenshots directory exists
os.makedirs("screenshots", exist_ok=True)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route("/capture", methods=["GET"])
def capture_chart():
    """Generate a mock chart screenshot."""
    symbol = request.args.get("symbol", "BTC/USD")
    timeframe = request.args.get("timeframe", "1h")
    
    logger.info(f"Capturing chart for {symbol} on {timeframe} timeframe")
    
    # Generate or retrieve a mock chart
    img_path = generate_mock_chart(symbol, timeframe)
    
    # Return the chart image
    return send_file(img_path, mimetype='image/png')

def generate_mock_chart(symbol, timeframe):
    """Generate a mock price chart image."""
    filename = f"screenshots/{symbol.replace('/', '_')}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # Create a blank image with white background
    width, height = 1280, 800
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw chart grid
    for i in range(0, width, 50):
        # Vertical lines
        draw.line([(i, 0), (i, height)], fill=(230, 230, 230), width=1)
    
    for i in range(0, height, 50):
        # Horizontal lines
        draw.line([(0, i), (width, i)], fill=(230, 230, 230), width=1)
    
    # Generate random price data
    num_points = 100
    x_points = np.linspace(50, width-50, num_points)
    
    # Create a somewhat realistic price movement
    y_base = height/2
    volatility = random.uniform(50, 100)
    trend = random.uniform(-0.3, 0.3)
    
    price_points = []
    current_price = y_base
    
    for i in range(num_points):
        # Random walk with trend
        current_price += random.normalvariate(trend, 1) * volatility / 10
        # Keep within reasonable bounds
        current_price = max(min(current_price, height-100), 100)
        price_points.append(current_price)
    
    # Draw price line
    points = list(zip(x_points, price_points))
    for i in range(1, len(points)):
        draw.line([points[i-1], points[i]], fill=(0, 100, 255), width=2)
    
    # Draw candlesticks
    for i in range(0, num_points, 3):
        x = x_points[i]
        open_price = price_points[i] + random.normalvariate(0, 1) * 20
        close_price = price_points[i] + random.normalvariate(0, 1) * 20
        high_price = max(open_price, close_price) + abs(random.normalvariate(0, 1) * 10)
        low_price = min(open_price, close_price) - abs(random.normalvariate(0, 1) * 10)
        
        # Candlestick color
        candle_color = (0, 200, 0) if close_price > open_price else (255, 0, 0)
        
        # Draw candlestick
        draw.line([(x, low_price), (x, high_price)], fill=(0, 0, 0), width=1)
        draw.rectangle([(x-5, open_price), (x+5, close_price)], fill=candle_color)
    
    # Draw title
    draw.rectangle([(0, 0), (width, 50)], fill=(240, 240, 240))
    draw.text((20, 20), f"{symbol} - {timeframe} Chart", fill=(0, 0, 0))
    
    # Add some indicator labels
    draw.text((width-150, 20), "RSI: 56.78", fill=(0, 0, 0))
    draw.text((width-150, 40), "MACD: Bullish", fill=(0, 100, 0))
    
    # Save the image
    img.save(filename)
    logger.info(f"Generated mock chart: {filename}")
    
    return filename

@app.route("/configure", methods=["POST"])
def configure_chart():
    """Mock endpoint to configure chart settings."""
    data = request.json
    
    symbol = data.get("symbol", "BTC/USD")
    timeframe = data.get("timeframe", "1h")
    indicators = data.get("indicators", ["RSI", "MACD", "Volume"])
    
    logger.info(f"Configuring chart for {symbol} on {timeframe} with indicators: {indicators}")
    
    return jsonify({
        "status": "success",
        "message": "Chart configured successfully",
        "data": {
            "symbol": symbol,
            "timeframe": timeframe,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3333))
    app.run(host="0.0.0.0", port=port) 