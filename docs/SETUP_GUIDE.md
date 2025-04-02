# Bluefin AI Agent Trader - Setup Guide

## Prerequisites

- Python 3.8+
- pip package manager
- (Optional) Virtual environment recommended

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/bluefin-ai-agent-trader.git
cd bluefin-ai-agent-trader
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Secrets Management

### Configuring Secrets

The project uses a robust Secure Secrets Manager with multiple backend support. You have several options for managing secrets:

#### 1. Local Encrypted File Backend (Default)

- Secrets are stored in encrypted files in the `secure_secrets_storage` directory
- Provides file-level encryption and access controls
- Ideal for local development and small-scale deployments

#### 2. Environment Variable Backend

- Secrets are encrypted and stored in environment variables
- Suitable for containerized and cloud environments
- Minimal filesystem footprint

#### 3. HashiCorp Vault Backend

- Enterprise-grade secrets management
- Dynamic secret generation
- Advanced access controls
- Recommended for production environments

### Configuration Example

```python
from secure_secrets import SecureSecretsManager, BackendType

# Default configuration (local file backend)
secrets_manager = SecureSecretsManager()

# Vault backend configuration
secrets_manager = SecureSecretsManager(
    default_backend=BackendType.VAULT,
    backends={
        BackendType.VAULT: {
            'vault_url': 'https://vault.example.com',
            'vault_token': 'your-vault-token',
            'mount_point': 'secret'
        }
    }
)
```

### Storing Secrets

```python
# Store API key
secrets_manager.store_secret('bluefin_api_key', 'your-secret-api-key')

# Store trading credentials in Vault
secrets_manager.store_secret(
    'trading_credentials', 
    'sensitive-trading-credentials',
    backend_type=BackendType.VAULT
)
```

### Retrieving Secrets

```python
# Retrieve API key
api_key = secrets_manager.retrieve_secret('bluefin_api_key')

# Retrieve trading credentials from Vault
vault_credentials = secrets_manager.retrieve_secret(
    'trading_credentials', 
    backend_type=BackendType.VAULT
)
```

## Environment Configuration

### 1. Create Environment Files

Create `.env.local`, `.env.staging`, and `.env.production` files based on `.env.template`:

```bash
cp .env.template .env.local
```

### 2. Configure Environment Variables

Edit the `.env.local` file with your specific configuration:

```
# Bluefin API Configuration
BLUEFIN_API_KEY=your-api-key
BLUEFIN_API_SECRET=your-api-secret

# Trading Configuration
TRADING_STRATEGY=default
MAX_TRADE_AMOUNT=1000

# Logging Configuration
LOG_LEVEL=INFO
```

## Running the Application

### Development Mode

```bash
python bluefin_trader.py
```

### Testing

```bash
pytest tests/
```

## Deployment

### Docker Deployment

```bash
docker-compose up --build
```

### Nix Deployment

```bash
nix-build
nix-shell
```

## Security Best Practices

1. Never commit secrets to version control
2. Use environment-specific configurations
3. Rotate secrets regularly
4. Implement least privilege access
5. Monitor and audit secret access

## Troubleshooting

- Ensure all dependencies are installed
- Check environment variable configurations
- Review logs for detailed error information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your project's license]