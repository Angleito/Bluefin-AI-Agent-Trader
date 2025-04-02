import os
import json
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from core.signal_processor import SignalProcessor
from core.trade_executor import TradeExecutor
from config.config import WebhookConfig

class WebhookService:
    """
    Webhook Service for processing TradingView and other trading alerts.
    Handles webhook validation, parsing, and signal processing.
    """

    def __init__(self, config: Optional[WebhookConfig] = None):
        """
        Initialize Webhook Service with configuration.
        
        :param config: Webhook configuration object
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default configuration with fallback
        self.config = config or WebhookConfig()
        
        # Core processing components
        self.signal_processor = SignalProcessor()
        self.trade_executor = TradeExecutor()
        
        # Rate limiting and security
        self.max_requests_per_minute = 60
        self.allowed_ip_ranges = self.config.allowed_ip_ranges
        
        # Create FastAPI app for webhook handling
        self.app = FastAPI(title="Trading Webhook Service")
        self._setup_routes()

    def _setup_routes(self):
        """
        Set up webhook routes for the FastAPI application.
        """
        @self.app.post("/webhook")
        async def handle_webhook(request: Request):
            """
            Main webhook endpoint for processing trading alerts.
            
            :param request: Incoming HTTP request
            :return: Webhook processing result
            """
            try:
                # Validate request source
                await self._validate_request_source(request)
                
                # Verify webhook signature
                await self._verify_signature(request)
                
                # Parse webhook payload
                payload = await request.json()
                self.logger.info(f"Received webhook payload: {payload}")
                
                # Process webhook signal
                signal = self._process_webhook_signal(payload)
                
                # Execute trade based on signal
                trade_result = await self._execute_trade(signal)
                
                return JSONResponse(
                    status_code=200, 
                    content={
                        "status": "success", 
                        "trade_id": trade_result.get('id'),
                        "signal": signal
                    }
                )
            
            except HTTPException as http_error:
                return JSONResponse(
                    status_code=http_error.status_code, 
                    content={"error": str(http_error.detail)}
                )
            
            except Exception as e:
                self.logger.error(f"Webhook processing error: {e}")
                return JSONResponse(
                    status_code=500, 
                    content={"error": "Internal server error"}
                )

    async def _validate_request_source(self, request: Request):
        """
        Validate the source of the incoming webhook request.
        
        :param request: Incoming HTTP request
        :raises HTTPException: If request source is not allowed
        """
        client_ip = request.client.host
        
        # Check IP range restrictions
        if self.allowed_ip_ranges and not any(
            self._ip_in_range(client_ip, allowed_range) 
            for allowed_range in self.allowed_ip_ranges
        ):
            raise HTTPException(
                status_code=403, 
                detail=f"Unauthorized source IP: {client_ip}"
            )

    async def _verify_signature(self, request: Request):
        """
        Verify the webhook signature for authenticity.
        
        :param request: Incoming HTTP request
        :raises HTTPException: If signature verification fails
        """
        signature_header = request.headers.get('X-Signature')
        if not signature_header:
            raise HTTPException(
                status_code=401, 
                detail="Missing signature header"
            )
        
        # Get raw request body
        body = await request.body()
        
        # Compute expected signature
        expected_signature = hmac.new(
            self.config.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(
                status_code=403, 
                detail="Invalid webhook signature"
            )

    def _process_webhook_signal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the webhook payload into a trading signal.
        
        :param payload: Webhook payload dictionary
        :return: Processed trading signal
        """
        try:
            # Validate payload against known formats
            signal = self.signal_processor.process_tradingview_alert(payload)
            
            if not signal:
                raise ValueError("Invalid or unsupported webhook format")
            
            return signal
        
        except ValidationError as ve:
            self.logger.warning(f"Webhook payload validation error: {ve}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid webhook payload"
            )

    async def _execute_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade based on processed signal.
        
        :param signal: Processed trading signal
        :return: Trade execution result
        """
        try:
            return await self.trade_executor.execute_trade(signal)
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Trade execution failed"
            )

    def _ip_in_range(self, ip: str, ip_range: str) -> bool:
        """
        Check if an IP is within a specified range.
        
        :param ip: IP address to check
        :param ip_range: IP range in CIDR notation
        :return: Whether IP is in range
        """
        import ipaddress
        try:
            return ipaddress.ip_address(ip) in ipaddress.ip_network(ip_range, strict=False)
        except ValueError:
            return False

    def start_service(self, host: str = '0.0.0.0', port: int = 8000):
        """
        Start the webhook service.
        
        :param host: Host to bind the service
        :param port: Port to listen on
        """
        import uvicorn
        uvicorn.run(
            self.app, 
            host=host, 
            port=port, 
            log_level="info"
        )