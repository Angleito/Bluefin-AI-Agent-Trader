import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """
    Configuration management class for Bluefin AI Agent Trader.
    Handles loading and validating configuration from multiple sources.
    """
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        """Singleton pattern implementation"""
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration by loading from different sources"""
        if not self._config:
            self.load_config()

    def load_config(self, config_path: str = None):
        """
        Load configuration from environment variables and JSON file.
        
        :param config_path: Optional path to JSON configuration file
        """
        # Load environment variables
        load_dotenv()

        # Load JSON configuration
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        try:
            with open(config_path, 'r') as config_file:
                self._config.update(json.load(config_file))
        except FileNotFoundError:
            print(f"Warning: Configuration file {config_path} not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file {config_path}")

        # Override with environment variables
        self._override_with_env_vars()
        
        # Validate configuration
        self.validate_config()

    def _override_with_env_vars(self):
        """
        Override configuration with environment variables.
        Environment variables take precedence over config file.
        """
        for key, value in os.environ.items():
            # Convert environment variables to appropriate types
            if key.upper().startswith('BLUEFIN_'):
                config_key = key.lower().replace('bluefin_', '')
                try:
                    # Try to parse as JSON if possible
                    parsed_value = json.loads(value)
                    self._config[config_key] = parsed_value
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, use the string value
                    self._config[config_key] = value

    def validate_config(self):
        """
        Validate required configuration parameters.
        Raises ValueError if any required parameters are missing.
        """
        required_params = [
            'trading_api_key', 
            'trading_api_secret', 
            'risk_max_loss_percentage',
            'trading_symbol'
        ]

        for param in required_params:
            if param not in self._config or not self._config[param]:
                raise ValueError(f"Missing required configuration parameter: {param}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.
        
        :param key: Configuration key
        :param default: Default value if key is not found
        :return: Configuration value or default
        """
        return self._config.get(key, default)

    def update(self, key: str, value: Any):
        """
        Dynamically update a configuration value.
        
        :param key: Configuration key to update
        :param value: New value for the key
        """
        self._config[key] = value
        # Optional: You could add a method to persist changes to file if needed

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.
        
        :return: Configuration dictionary
        """
        return self._config.copy()

# Create a global configuration instance
config = Config()