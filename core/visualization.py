import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from services.screenshot_service import ScreenshotService
from config.config import TRADING_PARAMS

class Visualization:
    def __init__(self, screenshot_service: Optional[ScreenshotService] = None):
        """
        Initialize Visualization with screenshot service and logging
        
        :param screenshot_service: Service for capturing and managing screenshots
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Use provided service or create a new one
        self.screenshot_service = screenshot_service or ScreenshotService()
        
        # Visualization output directory
        self.output_dir = TRADING_PARAMS.get(
            'visualization_output_dir', 
            os.path.join(os.getcwd(), 'trade_visualizations')
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def create_trade_history_chart(self, trade_history: List[Dict[str, Any]]) -> str:
        """
        Create a comprehensive trade history visualization
        
        :param trade_history: List of trade records
        :return: Path to generated chart image
        """
        try:
            # Convert trade history to DataFrame
            df = pd.DataFrame(trade_history)
            
            # Set up the plot
            plt.figure(figsize=(12, 6))
            plt.title('Trade Performance History')
            
            # Plot trade entries and exits
            plt.scatter(
                df[df['type'] == 'LONG'].index, 
                df[df['type'] == 'LONG']['entry_price'], 
                color='green', 
                label='Long Entries'
            )
            plt.scatter(
                df[df['type'] == 'SHORT'].index, 
                df[df['type'] == 'SHORT']['entry_price'], 
                color='red', 
                label='Short Entries'
            )
            
            # Add performance metrics
            plt.xlabel('Trade Number')
            plt.ylabel('Entry Price')
            plt.legend()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'trade_history_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            
            plt.savefig(filepath)
            plt.close()
            
            self.logger.info(f"Trade history chart saved: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Failed to create trade history chart: {e}")
            raise

    def create_performance_metrics_chart(self, performance_data: Dict[str, Any]) -> str:
        """
        Create a performance metrics visualization
        
        :param performance_data: Dictionary of performance metrics
        :return: Path to generated chart image
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.title('Trading Performance Metrics')
            
            # Bar chart of key performance indicators
            metrics = {
                'Total Profit': performance_data.get('total_profit', 0),
                'Win Rate': performance_data.get('win_rate', 0) * 100,
                'Max Drawdown': performance_data.get('max_drawdown', 0) * 100,
                'Sharpe Ratio': performance_data.get('sharpe_ratio', 0)
            }
            
            plt.bar(metrics.keys(), metrics.values())
            plt.ylabel('Value')
            plt.xticks(rotation=45)
            
            # Add value labels on top of each bar
            for i, (metric, value) in enumerate(metrics.items()):
                plt.text(i, value, f'{value:.2f}', ha='center', va='bottom')
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'performance_metrics_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            
            plt.tight_layout()
            plt.savefig(filepath)
            plt.close()
            
            self.logger.info(f"Performance metrics chart saved: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Failed to create performance metrics chart: {e}")
            raise

    def create_risk_analysis_chart(self, risk_data: Dict[str, Any]) -> str:
        """
        Create a risk analysis visualization
        
        :param risk_data: Dictionary of risk-related metrics
        :return: Path to generated chart image
        """
        try:
            plt.figure(figsize=(10, 6))
            plt.title('Risk Analysis')
            
            # Pie chart of risk allocation
            risk_allocation = {
                'Position Risk': risk_data.get('position_risk', 0) * 100,
                'Unrealized PNL': risk_data.get('unrealized_pnl', 0) * 100,
                'Available Balance': (1 - risk_data.get('position_risk', 0) - risk_data.get('unrealized_pnl', 0)) * 100
            }
            
            plt.pie(
                list(risk_allocation.values()), 
                labels=list(risk_allocation.keys()), 
                autopct='%1.1f%%'
            )
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'risk_analysis_{timestamp}.png'
            filepath = os.path.join(self.output_dir, filename)
            
            plt.tight_layout()
            plt.savefig(filepath)
            plt.close()
            
            self.logger.info(f"Risk analysis chart saved: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Failed to create risk analysis chart: {e}")
            raise

    def export_chart(self, chart_path: str, export_format: str = 'png') -> str:
        """
        Export a chart to a specific format
        
        :param chart_path: Path to the source chart image
        :param export_format: Desired export format
        :return: Path to exported chart
        """
        try:
            # Use screenshot service to handle export
            exported_path = self.screenshot_service.convert_image(
                chart_path, 
                export_format
            )
            
            self.logger.info(f"Chart exported: {exported_path}")
            return exported_path
        
        except Exception as e:
            self.logger.error(f"Failed to export chart: {e}")
            raise