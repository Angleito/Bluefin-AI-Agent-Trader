import os
import base64
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecretsManager:
    """
    A secure secrets management system for handling sensitive configuration data.
    
    Features:
    - Encryption of secrets at rest
    - Flexible secret loading from files or environment variables
    - Secure key derivation
    - Logging for security events
    """
    
    def __init__(self, 
                 secrets_file: Optional[str] = None, 
                 encryption_key: Optional[str] = None,
                 salt: Optional[bytes] = None):
        """
        Initialize the SecretsManager.
        
        :param secrets_file: Path to the secrets file (optional)
        :param encryption_key: Master encryption key (optional)
        :param salt: Cryptographic salt for key derivation (optional)
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - SecretsManager - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Set up salt and key
        self.salt = salt or os.urandom(16)
        self.encryption_key = self._derive_key(encryption_key)
        self.fernet = Fernet(self.encryption_key)
        
        # Load secrets
        self.secrets: Dict[str, str] = {}
        if secrets_file:
            self.load_secrets_from_file(secrets_file)
        
    def _derive_key(self, password: Optional[str] = None) -> bytes:
        """
        Derive a secure encryption key using PBKDF2.
        
        :param password: Optional master password
        :return: Base64 encoded Fernet key
        """
        # Use system-generated key if no password provided
        if not password:
            password = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Key derivation function
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def load_secrets_from_file(self, file_path: str) -> None:
        """
        Load encrypted secrets from a file.
        
        :param file_path: Path to the encrypted secrets file
        """
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.secrets = eval(decrypted_data.decode())
            self.logger.info(f"Successfully loaded secrets from {file_path}")
        except FileNotFoundError:
            self.logger.warning(f"Secrets file not found: {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading secrets: {e}")
            raise
    
    def load_secrets_from_env(self, secret_keys: Optional[list] = None) -> None:
        """
        Load secrets from environment variables.
        
        :param secret_keys: Optional list of specific secret keys to load
        """
        try:
            if secret_keys is None:
                # Load all uppercase environment variables as potential secrets
                secret_keys = [key for key in os.environ.keys() if key.isupper()]
            
            for key in secret_keys:
                value = os.environ.get(key)
                if value:
                    self.secrets[key] = value
            
            self.logger.info(f"Loaded {len(self.secrets)} secrets from environment")
        except Exception as e:
            self.logger.error(f"Error loading secrets from environment: {e}")
            raise
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret by key.
        
        :param key: Secret key to retrieve
        :param default: Default value if secret not found
        :return: Secret value or default
        """
        return self.secrets.get(key, default)
    
    def set_secret(self, key: str, value: str) -> None:
        """
        Set a secret value.
        
        :param key: Secret key
        :param value: Secret value
        """
        self.secrets[key] = value
        self.logger.info(f"Secret '{key}' set successfully")
    
    def save_secrets_to_file(self, file_path: str) -> None:
        """
        Save encrypted secrets to a file.
        
        :param file_path: Path to save the encrypted secrets
        """
        try:
            encrypted_data = self.fernet.encrypt(str(self.secrets).encode())
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            self.logger.info(f"Successfully saved secrets to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving secrets: {e}")
            raise
    
    def clear_secrets(self) -> None:
        """
        Clear all loaded secrets.
        """
        self.secrets.clear()
        self.logger.info("All secrets cleared")

# Example usage and configuration
def get_secrets_manager(
    secrets_file: Optional[str] = None, 
    encryption_key: Optional[str] = None
) -> SecretsManager:
    """
    Convenience factory method to create a SecretsManager instance.
    
    :param secrets_file: Optional path to encrypted secrets file
    :param encryption_key: Optional master encryption key
    :return: Configured SecretsManager instance
    """
    manager = SecretsManager(
        secrets_file=secrets_file, 
        encryption_key=encryption_key
    )
    
    # Optionally load from environment as a fallback
    manager.load_secrets_from_env()
    
    return manager