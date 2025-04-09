# Bluefin AI Agent Trader Template

A template for building AI-powered trading agents for the Bluefin exchange on the Sui network. This template provides a foundation for developing algorithmic trading strategies using AI models for signal generation.

## 🚀 Features

- **AI-Powered Trading**: Leverage AI models for trading signal generation
- **Simulation Mode**: Test strategies in a simulated environment before risking real funds
- **Risk Management**: Built-in risk management with stop-loss and take-profit mechanisms
- **Docker & Nix Integration**: Completely isolated dependencies for production deployment
- **Modular Architecture**: Easily extend and customize components for your specific needs

## 📋 Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Nix with flakes enabled (optional, for reproducible builds)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bluefin-ai-agent-trader-template.git
cd bluefin-ai-agent-trader-template
```

### 2. Set Up Environment

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Edit the `.env` file to configure your environment. For testing, you can leave the default values which will run in simulation mode.

### 3. Install Dependencies

Using pip:

```bash
pip install -r requirements.txt
```

Using Poetry:

```bash
poetry install
```

### 4. Run in Simulation Mode

```bash
python main.py
```

This will start the trading agent in simulation mode, which doesn't require any API keys or real funds.

### 5. Docker Deployment

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## 🏗️ Architecture

The template is organized into several key components:

### Services

- **BluefinService**: Handles interaction with the Bluefin exchange API
- **AIAgentService**: Generates trading signals using AI models
- **StrategyService**: Orchestrates trading strategies and execution

### Configuration

- **Config**: Manages configuration from environment variables and JSON files

### Utilities

- **Logging**: Comprehensive logging for monitoring and debugging
- **Risk Management**: Tools for managing trading risk

## 🔧 Customization

### Adding New Strategies

1. Create a new strategy class in `services/strategies/`
2. Implement the strategy interface
3. Register the strategy in the `StrategyService`

### Integrating Different AI Models

1. Extend the `AIAgentService` with your model integration
2. Implement the signal generation interface
3. Configure the model parameters in `.env` or `config.json`

## 🔒 Security Best Practices

1. **Never commit sensitive information** like API keys or private keys to version control
2. Use environment variables or secure secret management for credentials
3. Run the application with minimal permissions
4. Regularly update dependencies to patch security vulnerabilities

## 🚢 Production Deployment

For production deployment, we recommend using the Nix-based Docker setup:

```bash
# Build the Docker image using Nix
cd nix
nix build .#docker-image

# Load the Docker image
docker load < result

# Run with Docker Compose
docker-compose -f docker/docker-compose.yml up -d
```

## 📊 Monitoring

The template includes basic monitoring capabilities:

- Logs are written to `logs/trader.log`
- Performance metrics are tracked and can be exposed via API
- Prometheus integration for metrics collection (optional)

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 📝 License

This template is released under the MIT License. See the LICENSE file for details.

## ⚠️ Disclaimer

This software is provided for educational and research purposes only. Trading cryptocurrencies involves significant risk. Always do your own research before trading with real funds.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
