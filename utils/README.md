# Secrets Manager

## Overview
The `SecretsManager` is a secure, flexible solution for managing sensitive configuration data in the Bluefin AI Agent Trader project. It provides robust encryption, secure key management, and multiple methods for loading and storing secrets.

## Features

- **Secure Encryption**: Uses Fernet symmetric encryption with PBKDF2 key derivation
- **Flexible Secret Loading**: 
  - Load secrets from encrypted files
  - Load secrets from environment variables
  - Manual secret setting and retrieval
- **Comprehensive Logging**: Detailed logging of secret management operations
- **Error Handling**: Robust error handling and logging for security events

## Installation Dependencies

Install the required cryptography library:
```bash
pip install cryptography
```

## Usage Examples

### Basic Initialization

```python
from utils.secrets_manager import get_secrets_manager

# Initialize with default settings
secrets_manager = get_secrets_manager()

# Initialize with a specific secrets file and encryption key
secrets_manager = get_secrets_manager(
    secrets_file='path/to/secrets.enc', 
    encryption_key='your_master_password'
)
```

### Loading and Retrieving Secrets

```python
# Load secrets from environment variables
secrets_manager.load_secrets_from_env()

# Set a new secret
secrets_manager.set_secret('API_KEY', 'your_secret_api_key')

# Retrieve a secret
api_key = secrets_manager.get_secret('API_KEY')
```

### Saving Encrypted Secrets

```python
# Save current secrets to an encrypted file
secrets_manager.save_secrets_to_file('path/to/secrets.enc')

# Load secrets from the encrypted file later
secrets_manager.load_secrets_from_file('path/to/secrets.enc')
```

## Security Best Practices

1. **Never Commit Secrets**: Keep secrets files out of version control
2. **Use Strong Encryption Keys**: Use complex, unique master passwords
3. **Rotate Secrets Regularly**: Periodically update and rotate sensitive credentials
4. **Limit Secret Exposure**: Only load and use secrets when absolutely necessary

## Error Handling

The `SecretsManager` provides comprehensive logging. Check log outputs for any issues during secret management operations.

## Recommended Workflow

1. Use environment variables as the primary source of secrets
2. Provide an optional encrypted secrets file for additional security
3. Use the `get_secrets_manager()` factory method for consistent initialization

## Compatibility

Compatible with Python 3.7+ and requires the `cryptography` library.