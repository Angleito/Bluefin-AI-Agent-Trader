import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from playwright.async_api import async_playwright
import cv2
import numpy as np
from PIL import Image

class ScreenshotService:
    """
    Screenshot Service for capturing, storing, and managing trading chart screenshots.
    Provides advanced browser automation and image processing capabilities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Screenshot Service with configuration.
        
        :param config: Configuration dictionary for screenshot service
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default configuration with fallback
        self.config = config or {
            'screenshot_dir': os.getenv('SCREENSHOT_DIR', 'screenshots'),
            'tradingview_base_url': 'https://www.tradingview.com/chart/',
            'max_retries': 3,
            'timeout': 60000,  # milliseconds
            'browsers': ['chromium', 'firefox', 'webkit']
        }
        
        # Ensure screenshot directory exists
        os.makedirs(self.config['screenshot_dir'], exist_ok=True)
        
        # Tracking screenshot metadata
        self.screenshot_history: List[Dict[str, Any]] = []

    async def capture_chart(self, 
                             symbol: str, 
                             timeframe: str, 
                             browser_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a TradingView chart screenshot with advanced handling.
        
        :param symbol: Trading pair or stock symbol
        :param timeframe: Chart timeframe (1m, 5m, 1h, etc.)
        :param browser_type: Specific browser to use (optional)
        :return: Screenshot metadata
        """
        for attempt in range(self.config['max_retries']):
            try:
                async with async_playwright() as p:
                    # Select browser dynamically
                    browser_types = {
                        'chromium': p.chromium,
                        'firefox': p.firefox,
                        'webkit': p.webkit
                    }
                    selected_browser = (
                        browser_types.get(browser_type) or 
                        browser_types[self.config['browsers'][0]]
                    )
                    
                    # Launch browser
                    browser = await selected_browser.launch(
                        headless=True,  # Run in background
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                    
                    # Create new browser context and page
                    context = await browser.new_context()
                    page = await context.new_page()
                    
                    # Construct TradingView URL
                    url = (
                        f"{self.config['tradingview_base_url']}?"
                        f"symbol={symbol}&interval={timeframe}"
                    )
                    
                    # Navigate and wait for chart
                    await page.goto(url, timeout=self.config['timeout'])
                    await page.wait_for_selector(".chart-container", timeout=self.config['timeout'])
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{symbol}_{timeframe}_{timestamp}.png"
                    filepath = os.path.join(self.config['screenshot_dir'], filename)
                    
                    # Capture screenshot
                    await page.screenshot(path=filepath, full_page=True)
                    
                    # Close browser resources
                    await browser.close()
                    
                    # Process and validate screenshot
                    screenshot_metadata = self._process_screenshot(filepath, symbol, timeframe)
                    
                    return screenshot_metadata
            
            except Exception as e:
                self.logger.warning(f"Screenshot capture attempt {attempt + 1} failed: {e}")
                if attempt == self.config['max_retries'] - 1:
                    raise RuntimeError(f"Failed to capture screenshot for {symbol}")
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)

    def _process_screenshot(self, filepath: str, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Process and validate captured screenshot.
        
        :param filepath: Path to screenshot file
        :param symbol: Trading symbol
        :param timeframe: Chart timeframe
        :return: Screenshot metadata
        """
        try:
            # Read image
            image = cv2.imread(filepath)
            
            # Basic image quality checks
            height, width = image.shape[:2]
            file_size = os.path.getsize(filepath)
            
            # Compute image quality metrics
            grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            variance_of_laplacian = cv2.Laplacian(grayscale, cv2.CV_64F).var()
            
            # Metadata dictionary
            metadata = {
                'filepath': filepath,
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'width': width,
                'height': height,
                'file_size': file_size,
                'image_quality_score': variance_of_laplacian
            }
            
            # Store in history
            self.screenshot_history.append(metadata)
            
            # Limit history size
            if len(self.screenshot_history) > 100:
                self.screenshot_history = self.screenshot_history[-100:]
            
            return metadata
        
        except Exception as e:
            self.logger.error(f"Screenshot processing failed: {e}")
            raise

    def get_screenshot_history(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve screenshot history, optionally filtered by symbol.
        
        :param symbol: Optional symbol to filter screenshots
        :return: List of screenshot metadata
        """
        if symbol:
            return [
                screenshot for screenshot in self.screenshot_history 
                if screenshot['symbol'] == symbol
            ]
        return self.screenshot_history

    def annotate_screenshot(self, 
                             filepath: str, 
                             annotations: List[Dict[str, Any]]) -> str:
        """
        Annotate a screenshot with trade or analysis information.
        
        :param filepath: Path to screenshot file
        :param annotations: List of annotation details
        :return: Path to annotated screenshot
        """
        try:
            # Open image
            image = Image.open(filepath)
            draw = ImageDraw.Draw(image)
            
            # Add annotations
            for annotation in annotations:
                text = annotation.get('text', '')
                position = annotation.get('position', (10, 10))
                color = annotation.get('color', (255, 0, 0))  # Red
                font_size = annotation.get('font_size', 20)
                
                # Create font
                font = ImageFont.truetype("arial.ttf", font_size)
                draw.text(position, text, font=font, fill=color)
            
            # Save annotated image
            annotated_filepath = filepath.replace('.png', '_annotated.png')
            image.save(annotated_filepath)
            
            return annotated_filepath
        
        except Exception as e:
            self.logger.error(f"Screenshot annotation failed: {e}")
            raise