# BluefinAI Agent Trader (Mock Demo)

A simplified demonstration of the BluefinAI Agent Trader system architecture. This is a mock version for showcase purposes only.

## System Overview

This mock implementation demonstrates the architecture of an automated cryptocurrency trading system that integrates with trading APIs, technical analysis tools, and AI-powered decision making.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Signal Source  │─────▶│  Webhook        │─────▶│  Trading        │
│  (TradingView)  │      │  Service        │      │  Service        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  AI Analysis    │◀─────│  Chart Capture  │◀─────│  Position       │
│  Service        │─────▶│  Service        │      │  Monitor        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Components

1. **Trading Service**: Handles interactions with exchange APIs
2. **Webhook Service**: Receives external trading signals
3. **Chart Capture Service**: Screenshots and captures chart data
4. **AI Analysis Service**: Analyzes market data using AI models
5. **Position Monitor**: Tracks and manages trading positions

## Setup and Usage

This is a demonstration project. For setup instructions, see:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
docker-compose up -d
```

## Important Note

⚠️ This is a non-functional MOCK implementation for demonstration purposes only. It contains no actual trading logic or API connections. 