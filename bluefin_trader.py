#!/usr/bin/env python3
"""
Bluefin AI Agent Trader - Main Entry Point

This script serves as the central orchestrator for the Bluefin AI Agent Trader,
managing service initialization, configuration, and runtime execution.
"""

import os
import sys
import argparse
import asyncio
import logging
import signal
from typing import Dict, List, Any, Optional
from importlib import import_module

# Configure base logging before other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bluefin_trader.log', mode='a')
    ]
)
logger = logging.getLogger('BluefinTrader')

class BluefinTrader:
    """
    Main orchestrator for the Bluefin AI Agent Trader.
    Manages service initialization, configuration, and runtime execution.
    """

    def __init__(self, config_path: Optional[str] = None, log_level: str = 'INFO'):
        """
        Initialize the Bluefin Trader with configuration and logging setup.

        :param config_path: Path to configuration file
        :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.config_path = config_path or os.path.join('config', 'config.json')
        self.config: Dict[str, Any] = self._load_config()
        
        # Set log level
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        logging.getLogger().setLevel(log_level_map.get(log_level.upper(), logging.INFO))

        self.services: Dict[str, Any] = {}
        self.is_running = False

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        :return: Configuration dictionary
        """
        try:
            import json
            with open(self.config_path, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {self.config_path}")
            raise

    async def _initialize_services(self) -> None:
        """
        Dynamically import and initialize services from services directory.
        """
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        service_files = [f[:-3] for f in os.listdir(services_dir) if f.endswith('_service.py')]

        for service_name in service_files:
            try:
                module = import_module(f'services.{service_name}')
                service_class = getattr(module, ''.join(word.capitalize() for word in service_name.split('_')))
                
                # Initialize service with configuration
                service_config = self.config.get(service_name, {})
                service_instance = service_class(**service_config)
                
                # If service has async initialization, call it
                if hasattr(service_instance, 'initialize') and asyncio.iscoroutinefunction(service_instance.initialize):
                    await service_instance.initialize()
                
                self.services[service_name] = service_instance
                logger.info(f"Initialized service: {service_name}")
            
            except ImportError as e:
                logger.error(f"Failed to import service {service_name}: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize service {service_name}: {e}")

    async def run(self) -> None:
        """
        Main runtime method to start and manage services.
        """
        try:
            self.is_running = True
            await self._initialize_services()
            
            # Add your main trading logic or service coordination here
            logger.info("Bluefin AI Agent Trader is running...")
            
            # Keep the main coroutine alive
            while self.is_running:
                await asyncio.sleep(1)
        
        except Exception as e:
            logger.critical(f"Critical error in trader runtime: {e}")
            self.is_running = False
            raise

    def stop(self) -> None:
        """
        Gracefully stop all services and trader runtime.
        """
        logger.info("Stopping Bluefin AI Agent Trader...")
        self.is_running = False

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the Bluefin Trader.

    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Bluefin AI Agent Trader')
    parser.add_argument(
        '-c', '--config', 
        default=os.path.join('config', 'config.json'),
        help='Path to configuration file'
    )
    parser.add_argument(
        '-l', '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO', 
        help='Set the logging level'
    )
    return parser.parse_args()

def main():
    """
    Main entry point for the Bluefin AI Agent Trader.
    """
    args = parse_arguments()
    trader = BluefinTrader(config_path=args.config, log_level=args.log_level)

    # Setup signal handling for graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, trader.stop)

    try:
        loop.run_until_complete(trader.run())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down...")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        sys.exit(1)
    finally:
        loop.close()

if __name__ == '__main__':
    main()