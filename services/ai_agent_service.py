import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional

import anthropic
import openai  # For Perplexity
from core.signal_processor import SignalProcessor

class AIAgentService:
    """
    AI Agent Service for generating trading signals using multiple AI models.
    Handles signal generation, confidence scoring, and model fallback mechanisms.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI Agent Service with configuration and API clients.
        
        :param config: Configuration dictionary for AI models and parameters
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default configuration with fallback
        self.config = config or {
            'claude': {
                'model': 'claude-3-opus-20240229',
                'max_tokens': 4096,
                'temperature': 0.7
            },
            'perplexity': {
                'model': 'pplx-7b-online',
                'max_tokens': 4096,
                'temperature': 0.7
            }
        }
        
        # Initialize API clients
        self.claude_client = anthropic.AsyncAnthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.perplexity_client = openai.AsyncOpenAI(
            api_key=os.getenv('PERPLEXITY_API_KEY'),
            base_url='https://api.perplexity.ai/'
        )
        
        # Signal processor for further signal validation
        self.signal_processor = SignalProcessor()
        
        # Caching mechanism for frequent analyses
        self.analysis_cache = {}
        
        # Rate limiting configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    async def generate_trading_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a trading signal using AI models with fallback mechanism.
        
        :param market_data: Market data for analysis
        :return: Trading signal with direction, confidence, and reasoning
        """
        # Check cache first
        cache_key = self._generate_cache_key(market_data)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Try Claude first
        try:
            signal = await self._generate_claude_signal(market_data)
        except Exception as claude_error:
            self.logger.warning(f"Claude signal generation failed: {claude_error}")
            
            # Fallback to Perplexity
            try:
                signal = await self._generate_perplexity_signal(market_data)
            except Exception as perplexity_error:
                self.logger.error(f"Both Claude and Perplexity signal generation failed: {perplexity_error}")
                raise RuntimeError("Unable to generate trading signal from AI models")
        
        # Validate and process signal
        validated_signal = self.signal_processor.validate_signal(signal)
        
        # Cache the result
        self.analysis_cache[cache_key] = validated_signal
        
        return validated_signal

    async def _generate_claude_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal using Claude AI.
        
        :param market_data: Market data for analysis
        :return: Trading signal
        """
        claude_config = self.config['claude']
        prompt = self._build_analysis_prompt(market_data)
        
        for attempt in range(self.max_retries):
            try:
                response = await self.claude_client.messages.create(
                    model=claude_config['model'],
                    max_tokens=claude_config['max_tokens'],
                    temperature=claude_config['temperature'],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                return self._parse_ai_response(response.content[0].text)
            
            except Exception as e:
                self.logger.warning(f"Claude signal generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def _generate_perplexity_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal using Perplexity AI.
        
        :param market_data: Market data for analysis
        :return: Trading signal
        """
        perplexity_config = self.config['perplexity']
        prompt = self._build_analysis_prompt(market_data)
        
        for attempt in range(self.max_retries):
            try:
                response = await self.perplexity_client.chat.completions.create(
                    model=perplexity_config['model'],
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=perplexity_config['max_tokens'],
                    temperature=perplexity_config['temperature']
                )
                
                return self._parse_ai_response(response.choices[0].message.content)
            
            except Exception as e:
                self.logger.warning(f"Perplexity signal generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    def _build_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt for AI market analysis.
        
        :param market_data: Market data dictionary
        :return: Formatted prompt string
        """
        return f"""
        Perform a detailed market analysis and provide a precise trading signal.
        
        Market Data:
        - Symbol: {market_data.get('symbol', 'N/A')}
        - Current Price: {market_data.get('price', 'N/A')}
        - Technical Indicators: {json.dumps(market_data.get('indicators', {}))}
        - Historical Data: {json.dumps(market_data.get('historical_data', []))}
        
        Analysis Requirements:
        1. Determine trading direction (buy/sell/hold)
        2. Provide confidence score (0-1 scale)
        3. Explain reasoning behind the signal
        
        Response Format (JSON):
        {{
            "direction": "buy|sell|hold",
            "confidence": 0.0-1.0,
            "reasoning": "Detailed explanation of analysis"
        }}
        """

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response, extracting signal information.
        
        :param response_text: Raw text response from AI
        :return: Parsed signal dictionary
        """
        try:
            # Try direct JSON parsing
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback to extracting signal from text
            return self._extract_signal_from_text(response_text)

    def _extract_signal_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract trading signal from unstructured text.
        
        :param text: Unstructured text response
        :return: Extracted signal dictionary
        """
        # Implement advanced text parsing logic
        # This is a placeholder and should be enhanced with NLP techniques
        default_signal = {
            "direction": "hold",
            "confidence": 0.5,
            "reasoning": "Unable to parse precise signal from AI response"
        }
        
        # Basic keyword matching
        text = text.lower()
        if "buy" in text:
            default_signal["direction"] = "buy"
            default_signal["confidence"] = 0.7
        elif "sell" in text:
            default_signal["direction"] = "sell"
            default_signal["confidence"] = 0.7
        
        return default_signal

    def _generate_cache_key(self, market_data: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for market data.
        
        :param market_data: Market data dictionary
        :return: Unique cache key
        """
        return json.dumps(market_data, sort_keys=True)

    def clear_cache(self):
        """
        Clear the analysis cache to prevent stale data.
        """
        self.analysis_cache.clear()