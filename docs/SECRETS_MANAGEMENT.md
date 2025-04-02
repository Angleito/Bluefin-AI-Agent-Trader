# Secure Secrets Management

## Overview

The Secure Secrets Manager provides a comprehensive, flexible solution for managing sensitive information across different storage backends with advanced security features.

## Features

- **Multiple Backend Support**
  * Local encrypted file storage
  * Environment variable encryption
  * HashiCorp Vault integration

- **Advanced Security**
  * Strong encryption using Fernet symmetric encryption
  * Salted key derivation
  * Key rotation capabilities
  * Comprehensive audit logging

- **Flexible Configuration**
  * Easily switch between different secret storage backends
  * Configurable encryption and logging utilities

## Installation

Ensure you have the following dependencies:
- Python 3.8+
- `cryptography` library
- `hvac` library (for Vault backend)

```bash
pip install cryptography hvac
```

## Basic Usage

### Initializing the Secrets Manager

```python
from secure_secrets import SecureSecretsManager, BackendType

# Default configuration (local file backend)
secrets_manager = SecureSecretsManager()

# Custom configuration with Vault backend
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
# Store a secret in the default backend
api_key_event = secrets_manager.store_secret(
    'bluefin_api_key', 
    'your-secret-api-key-here'
)

# Store a secret in a specific backend
vault_secret_event = secrets_manager.store_secret(
    'trading_credentials', 
    'sensitive-trading-credentials',
    backend_type=BackendType.VAULT
)
```

### Retrieving Secrets

```python
# Retrieve from default backend
api_key = secrets_manager.retrieve_secret('bluefin_api_key')

# Retrieve from Vault backend
vault_credentials = secrets_manager.retrieve_secret(
    'trading_credentials', 
    backend_type=BackendType.VAULT
)
```

### Key Rotation

```python
# Rotate the master encryption key
rotation_event = secrets_manager.rotate_encryption_key()
```

### Deleting Secrets

```python
# Delete a secret from the default backend
delete_event = secrets_manager.delete_secret('bluefin_api_key')
```

## Backend Types

1. **Local Encrypted File Backend**
   - Stores secrets in encrypted files
   - Provides file-level access controls
   - Suitable for local development and small-scale deployments

2. **Environment Variable Backend**
   - Stores secrets in encrypted environment variables
   - Useful for containerized and cloud environments
   - Minimal filesystem footprint

3. **HashiCorp Vault Backend**
   - Enterprise-grade secrets management
   - Dynamic secret generation
   - Advanced access controls
   - Recommended for production environments

## Security Best Practices

1. **Never Hardcode Secrets**
   - Always use the Secrets Manager to handle sensitive information
   - Use environment variables or secure configuration management

2. **Implement Least Privilege**
   - Limit access to secrets based on specific roles and requirements
   - Rotate credentials regularly

3. **Audit and Monitor**
   - Review audit logs frequently
   - Set up alerts for suspicious secret access patterns

4. **Secure Key Management**
   - Rotate encryption keys periodically
   - Use strong, unique keys for each environment

## Error Handling

```python
from secure_secrets.exceptions import (
    SecretAccessError, 
    EncryptionError, 
    BackendConfigurationError
)

try:
    secret = secrets_manager.retrieve_secret('my_secret')
except SecretAccessError as e:
    # Handle secret retrieval errors
    print(f"Failed to access secret: {e}")
except EncryptionError as e:
    # Handle encryption-related errors
    print(f"Encryption error: {e}")
```

## Logging and Auditing

The Secrets Manager provides comprehensive audit logging:
- Tracks all secret management operations
- Generates unique event IDs for traceability
- Supports custom logging configurations

## Migration Guide

### From Environment Variables

1. Identify existing secrets in `.env` or environment variables
2. Use the Secrets Manager to store and manage these secrets
3. Update application code to use `retrieve_secret()` instead of direct environment variable access

## Troubleshooting

- Ensure all required dependencies are installed
- Check backend-specific configurations
- Review audit logs for detailed error information

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the project repository.

## License

[Specify your project's license]