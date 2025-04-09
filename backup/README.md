# Bluefin AI Agent Trader

## Overview

Bluefin AI Agent Trader is an advanced, modular trading bot designed to interact with the Bluefin exchange on the SUI blockchain. Leveraging artificial intelligence and sophisticated trading strategies, this bot provides an intelligent and flexible solution for cryptocurrency trading.

## Key Features

- **AI-Powered Trading**: Utilizes advanced AI algorithms to make informed trading decisions
- **Modular Architecture**: Flexible, service-based design for easy extensibility
- **Blockchain Integration**: Seamless interaction with the Bluefin exchange on the SUI blockchain
- **Comprehensive Risk Management**: Built-in risk assessment and mitigation strategies
- **Secure Deployment**: Docker and Nix-based infrastructure with robust security practices
- **Monitoring and Logging**: Integrated monitoring with Prometheus and Grafana

## Architecture

The Bluefin AI Agent Trader is built with a modular, service-oriented architecture:

### Core Components

1. **Trade Executor** (`core/trade_executor.py`):
   - Responsible for executing trading strategies
   - Manages trade entry and exit points
   - Implements risk management protocols

2. **Signal Processor** (`core/signal_processor.py`):
   - Analyzes market data
   - Generates trading signals
   - Integrates AI-driven insights

3. **Risk Manager** (`core/risk_manager.py`):
   - Monitors and manages trading risks
   - Implements stop-loss and take-profit mechanisms
   - Ensures capital preservation

### Services

- **Bluefin Service** (`services/bluefin_service.py`):
  - Handles direct interactions with the Bluefin exchange
  - Manages API communications
  - Handles authentication and transaction processing

- **AI Agent Service** (`services/ai_agent_service.py`):
  - Manages AI model interactions
  - Processes and generates trading recommendations
  - Continuous learning and strategy optimization

- **Position Service** (`services/position_service.py`):
  - Tracks and manages open positions
  - Provides real-time position analytics
  - Supports portfolio management

## Prerequisites

- Python 3.9+
- Nix (recommended for dependency management)
- Docker (optional, for containerized deployment)
- Bluefin Exchange API Credentials

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bluefin-ai-agent-trader.git
   cd bluefin-ai-agent-trader
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

### Nix-based Setup

```bash
nix develop  # Enter development environment
```

### Docker Deployment

```bash
docker-compose build
docker-compose up -d
```

## Configuration

1. Copy `.env.template` to `.env`
2. Fill in your Bluefin API credentials and other configuration parameters

### Configuration Options

- `BLUEFIN_API_KEY`: Your Bluefin exchange API key
- `TRADING_STRATEGY`: Select from predefined strategies or create custom
- `RISK_TOLERANCE`: Set risk management parameters
- `AI_MODEL_CONFIG`: Configure AI model settings

## Usage

### Running the Trader

```bash
python bluefin_trader.py
```

### Example Trading Strategies

The bot supports multiple trading strategies:
- Trend Following
- Mean Reversion
- Arbitrage
- Machine Learning-based Prediction

## Security Considerations

- Never commit sensitive information to version control
- Use external secret management
- Rotate API keys regularly
- Implement read-only file systems
- Use non-root containers

## Monitoring

The project includes integrated monitoring with:
- Prometheus for metrics collection
- Grafana for visualization and dashboards

Access Grafana at `http://localhost:3000`

## Deployment

### Nix Deployment

```bash
./scripts/deploy-nix.sh
```

### Docker Deployment

```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Support

For issues, feature requests, or support, please open an issue on the GitHub repository.

---

**Disclaimer**: Cryptocurrency trading involves significant risk. Use this bot responsibly and never invest more than you can afford to lose.