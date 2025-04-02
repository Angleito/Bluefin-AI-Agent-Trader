"""
Secure Secrets Manager Demonstration

This script showcases the capabilities of the SecureSecretsManager,
demonstrating various secret management operations across different backends.
"""

import os
from secure_secrets import (
    SecureSecretsManager, 
    BackendType
)
from secure_secrets.exceptions import SecretAccessError

def main():
    """
    Demonstrate the usage of the Secure Secrets Manager with multiple backends.
    """
    # Initialize the Secure Secrets Manager
    secrets_manager = SecureSecretsManager(
        default_backend=BackendType.LOCAL_FILE,
        backends={
            BackendType.VAULT: {
                'vault_url': os.getenv('VAULT_URL', 'https://vault.example.com'),
                'vault_token': os.getenv('VAULT_TOKEN'),
                'mount_point': 'secret'
            }
        }
    )

    # Demonstration of secret management operations
    try:
        # 1. Store a secret in the default local file backend
        api_key_event = secrets_manager.store_secret(
            'bluefin_api_key', 
            'your-secret-api-key-here'
        )
        print(f"API Key stored successfully. Event ID: {api_key_event}")

        # 2. Retrieve the secret from the default backend
        retrieved_api_key = secrets_manager.retrieve_secret('bluefin_api_key')
        print("API Key retrieved successfully.")

        # 3. Store a secret in the Vault backend
        vault_secret_event = secrets_manager.store_secret(
            'trading_credentials', 
            'sensitive-trading-credentials',
            backend_type=BackendType.VAULT
        )
        print(f"Trading credentials stored in Vault. Event ID: {vault_secret_event}")

        # 4. Retrieve the secret from Vault
        vault_credentials = secrets_manager.retrieve_secret(
            'trading_credentials', 
            backend_type=BackendType.VAULT
        )
        print("Trading credentials retrieved from Vault successfully.")

        # 5. Demonstrate key rotation
        rotation_event = secrets_manager.rotate_encryption_key()
        print(f"Encryption key rotated. Event ID: {rotation_event}")

        # 6. Delete a secret
        delete_event = secrets_manager.delete_secret('bluefin_api_key')
        print(f"API Key deleted. Event ID: {delete_event}")

    except SecretAccessError as e:
        print(f"Secret management error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()