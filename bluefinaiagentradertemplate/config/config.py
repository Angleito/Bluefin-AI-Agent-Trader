"""
Configuration Manager for Bluefin AI Agent Trader Template

This module handles loading, validating, and accessing configuration from
environment variables and JSON files.
"""

import os
import json
from typing import Dict, Any, Optional
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

    def load_config(self, config_path: Optional[str] = None):
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
        # Map environment variables to configuration keys
        env_mapping = {
            'BLUEFIN_NETWORK': 'bluefin_parameters.network',
            'BLUEFIN_PRIVATE_KEY': 'bluefin_parameters.private_key',
            'BLUEFIN_EXCHANGE': 'bluefin_parameters.exchange',
            'BLUEFIN_API_URL': 'bluefin_parameters.api_url',
            'BLUEFIN_MAX_RETRIES': 'bluefin_parameters.max_retries',
            'BLUEFIN_RETRY_DELAY': 'bluefin_parameters.retry_delay',
            'ANTHROPIC_API_KEY': 'ai_agent_parameters.anthropic_api_key',
            'PERPLEXITY_API_KEY': 'ai_agent_parameters.perplexity_api_key',
            'AI_CLAUDE_MODEL': 'ai_agent_parameters.claude_model',
            'AI_CLAUDE_MAX_TOKENS': 'ai_agent_parameters.claude_max_tokens',
            'AI_CLAUDE_TEMPERATURE': 'ai_agent_parameters.claude_temperature',
            'LOG_LEVEL': 'logging_parameters.log_level',
            'SIMULATION_MODE': 'simulation_parameters.enabled',
            'SIMULATION_INITIAL_BALANCE': 'simulation_parameters.initial_balance',
            'SIMULATION_VOLATILITY': 'simulation_parameters.volatility',
            'SIMULATION_TREND': 'simulation_parameters.trend'
        }
        
        for env_var, config_path in env_mapping.items():
            if env_var in os.environ:
                # Parse the value based on type
                value = os.environ[env_var]
                try:
                    # Try to convert to appropriate type
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif '.' in value and all(part.isdigit() for part in value.split('.', 1)):
                        value = float(value)
                except (ValueError, AttributeError):
                    pass  # Keep as string if conversion fails
                
                # Set the value in the config dictionary
                self._set_nested_value(config_path, value)

    def _set_nested_value(self, path: str, value: Any):
        """
        Set a value in a nested dictionary using a dot-separated path.
        
        :param path: Dot-separated path to the value
        :param value: Value to set
        """
        keys = path.split('.')
        current = self._config
        
        # Navigate to the nested location
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value

    def validate_config(self):
        """
        Validate required configuration parameters.
        In simulation mode, we don't require real API keys.
        """
        # Check if simulation mode is enabled
        simulation_enabled = self.get('simulation_parameters', {}).get('enabled', False)
        
        if not simulation_enabled:
            # These are only required if not in simulation mode
            required_params = [
                ('bluefin_parameters.private_key', "Bluefin private key"),
                ('ai_agent_parameters.anthropic_api_key', "Anthropic API key")
            ]
            
            for param_path, param_name in required_params:
                value = self._get_nested_value(param_path)
                if not value or value.startswith('YOUR_'):
                    print(f"Warning: {param_name} is not set. Some features may not work correctly.")

    def _get_nested_value(self, path: str, default: Any = None) -> Any:
        """
        Get a value from a nested dictionary using a dot-separated path.
        
        :param path: Dot-separated path to the value
        :param default: Default value if path doesn't exist
        :return: Value at the path or default
        """
        keys = path.split('.')
        current = self._config
        
        # Navigate to the nested location
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        
        return current

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.
        
        :param key: Configuration key
        :param default: Default value if key is not found
        :return: Configuration value or default
        """
        if '.' in key:
            return self._get_nested_value(key, default)
        return self._config.get(key, default)

    def is_simulation_mode(self) -> bool:
        """
        Check if simulation mode is enabled.
        
        :return: True if simulation mode is enabled, False otherwise
        """
        return self.get('simulation_parameters.enabled', False)

# Create a singleton instance
config = Config()
