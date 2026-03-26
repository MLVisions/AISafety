"""
Historical Data Visualization Agent
Creates comprehensive charts showing maximum available historical data for all assets
with interactive dropdowns for evidence supporting investment strategies
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from agents.utils.constants import COLORS, PALETTE, setup_plot_style

from .data_sources import get_all_asset_data
from .ticker_constants import get_ticker_display_name


class HistoricalDataVisualizationAgent:
    """
    Agent responsible for creating comprehensive historical data visualizations
    with maximum available time periods for all asset classes
    """

    def __init__(self, output_dir: str = "docs/images"):
        """
        Initialize the visualization agent

        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.historical_data: dict[str, dict[str, pd.DataFrame]] = {}
        self.data_summaries: dict[str, dict[str, Any]] = {}

    def fetch_all_historical_data(self, force_refresh: bool = False) -> dict[str, dict[str, pd.DataFrame]]:
        """
        Fetch maximum historical data for all supported tickers

        Args:
            force_refresh: Whether to force refresh even if data exists

        Returns:
            Nested dictionary: asset_class -> ticker -> DataFrame
        """
        if self.historical_data and not force_refresh:
            return self.historical_data

        print("Fetching maximum historical data for all assets...")
        self.historical_data = get_all_asset_data(max_history=True)

        # Generate data summaries
        self.data_summaries = {}
        for asset_class, asset_data in self.historical_data.items():
            self.data_summaries[asset_class] = {}
            for ticker, df in asset_data.items():
                if not df.empty:
                    start_date = df['Date'].min()
                    end_date = df['Date'].max()
                    years = (end_date - start_date).days / 365.25

                    self.data_summaries[asset_class][ticker] = {
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'years_of_data': round(years, 1),
                        'data_points': len(df)
                    }

        return self.historical_data

    def create_asset_class_visualization(self, asset_class: str, save_plots: bool = True) -> dict[str, str]:
        """
        Create comprehensive visualization for an entire asset class

        Args:
            asset_class: Asset class to visualize
            save_plots: Whether to save plots to disk

        Returns:
            Dictionary mapping chart types to file paths
        """
        if asset_class not in self.historical_data:
            raise ValueError(f"No data available for asset class: {asset_class}")

        asset_data = self.historical_data[asset_class]
        setup_plot_style()

        # Create multiple chart types
        chart_files = {}

        # 1. Individual asset charts (one per asset)
        for ticker, df in asset_data.items():
            if df.empty:
                continue

            fig, ax = plt.subplots(figsize=(14, 8))

            # Plot price over time
            ax.plot(df['Date'], df['Close'],
                   color=COLORS['primary_blue'], linewidth=2, alpha=0.8)

            # Format chart
            ax.set_title(f'{ticker} - Historical Price Data\n'
                        f'{self.data_summaries[asset_class][ticker]["start_date"]} to '
                        f'{self.data_summaries[asset_class][ticker]["end_date"]} '
                        f'({self.data_summaries[asset_class][ticker]["years_of_data"]} years)',
                        fontsize=16, fontweight='bold', pad=20)

            ax.set_xlabel('Year', fontweight='bold')
            ax.set_ylabel('Price (USD)', fontweight='bold')

            # Format x-axis
            years_span = self.data_summaries[asset_class][ticker]["years_of_data"]
            if years_span > 20:
                ax.xaxis.set_major_locator(mdates.YearLocator(5))
            elif years_span > 10:
                ax.xaxis.set_major_locator(mdates.YearLocator(2))
            else:
                ax.xaxis.set_major_locator(mdates.YearLocator())

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            # Add grid
            ax.grid(True, alpha=0.3)

            # Add annotation with key statistics
            current_price = df['Close'].iloc[-1]
            max_price = df['Close'].max()
            min_price = df['Close'].min()

            stats_text = (f'Current: ${current_price:.2f}\n'
                         f'Max: ${max_price:.2f}\n'
                         f'Min: ${min_price:.2f}\n'
                         f'Data Points: {len(df):,}')

            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=10,
                   bbox={'boxstyle': 'round', 'facecolor': COLORS['background'], 'alpha': 0.8})

            plt.tight_layout()

            if save_plots:
                filename = f'{asset_class}_{ticker.replace("^", "").replace("=", "_").replace("-", "_")}_historical.png'
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
                chart_files[f'{ticker}_individual'] = str(filepath)

            plt.close()

        # 2. Combined overview chart for asset class
        if len(asset_data) > 1:
            fig, ax = plt.subplots(figsize=(16, 10))

            colors = PALETTE

            for i, (ticker, df) in enumerate(asset_data.items()):
                if df.empty:
                    continue

                # Normalize to percentage change from first value for comparison
                normalized_prices = (df['Close'] / df['Close'].iloc[0] - 1) * 100

                color = colors[i % len(colors)]
                ax.plot(df['Date'], normalized_prices,
                       label=f'{ticker} ({self.data_summaries[asset_class][ticker]["years_of_data"]}y)',
                       color=color, linewidth=2, alpha=0.8)

            ax.set_title(f'{asset_class.title()} Asset Class - Normalized Performance Comparison\n'
                        'All assets normalized to percentage change from initial value',
                        fontsize=16, fontweight='bold', pad=20)

            ax.set_xlabel('Year', fontweight='bold')
            ax.set_ylabel('Percentage Change from Initial Value (%)', fontweight='bold')

            # Format x-axis
            all_dates = pd.concat([df['Date'] for df in asset_data.values() if not df.empty])
            date_range = (all_dates.max() - all_dates.min()).days / 365.25

            if date_range > 20:
                ax.xaxis.set_major_locator(mdates.YearLocator(5))
            elif date_range > 10:
                ax.xaxis.set_major_locator(mdates.YearLocator(2))
            else:
                ax.xaxis.set_major_locator(mdates.YearLocator())

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            plt.tight_layout()

            if save_plots:
                filename = f'{asset_class}_comparison_normalized.png'
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
                chart_files[f'{asset_class}_comparison'] = str(filepath)

            plt.close()

        return chart_files

    def create_all_visualizations(self) -> dict[str, dict[str, str]]:
        """
        Create visualizations for all asset classes

        Returns:
            Nested dictionary: asset_class -> chart_type -> file_path
        """
        if not self.historical_data:
            self.fetch_all_historical_data()

        all_charts = {}

        for asset_class in self.historical_data.keys():
            print(f"Creating visualizations for {asset_class}...")
            try:
                charts = self.create_asset_class_visualization(asset_class)
                all_charts[asset_class] = charts
            except Exception as e:
                print(f"Error creating visualizations for {asset_class}: {e}")
                continue

        return all_charts

    def generate_dropdown_data(self) -> dict[str, dict]:
        """
        Generate data structure for website dropdowns showing evidence charts

        Returns:
            Dictionary with dropdown options and metadata
        """
        dropdown_data: dict[str, Any] = {
            'asset_classes': {},
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'total_assets': sum(len(data) for data in self.historical_data.values()),
                'date_ranges': {}
            }
        }

        for asset_class, asset_data in self.historical_data.items():
            if not asset_data:
                continue

            dropdown_data['asset_classes'][asset_class] = {
                'display_name': asset_class.replace('_', ' ').title(),
                'assets': {}
            }

            min_start = None
            max_end = None

            for ticker, df in asset_data.items():
                if df.empty:
                    continue

                summary = self.data_summaries[asset_class][ticker]

                # Update overall date range
                start_date = pd.to_datetime(summary['start_date'])
                end_date = pd.to_datetime(summary['end_date'])

                if min_start is None or start_date < min_start:
                    min_start = start_date
                if max_end is None or end_date > max_end:
                    max_end = end_date

                dropdown_data['asset_classes'][asset_class]['assets'][ticker] = {
                    'display_name': self._get_display_name(ticker),
                    'start_date': summary['start_date'],
                    'end_date': summary['end_date'],
                    'years_of_data': summary['years_of_data'],
                    'chart_url': f'images/{asset_class}_{ticker.replace("^", "").replace("=", "_").replace("-", "_")}_historical.png'
                }

            # Set overall date range for asset class
            if min_start and max_end:
                dropdown_data['metadata']['date_ranges'][asset_class] = {
                    'earliest_start': min_start.strftime('%Y-%m-%d'),
                    'latest_end': max_end.strftime('%Y-%m-%d'),
                    'max_years': round((max_end - min_start).days / 365.25, 1)
                }

        return dropdown_data

    def _get_display_name(self, ticker: str) -> str:
        """Get human-readable display name for ticker."""
        return get_ticker_display_name(ticker)

    def save_dropdown_data(self, filename: str = "historical_data_dropdown.json") -> str:
        """
        Save dropdown data to JSON file for website integration

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        dropdown_data = self.generate_dropdown_data()
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(dropdown_data, f, indent=2)

        print(f"Saved dropdown data to {filepath}")
        return str(filepath)

    def analyze_trends(self) -> dict[str, dict]:
        """
        Analyze trends across all historical data

        Returns:
            Dictionary with trend analysis results
        """
        trend_analysis: dict[str, dict[str, Any]] = {}

        for asset_class, asset_data in self.historical_data.items():
            trend_analysis[asset_class] = {}

            for ticker, df in asset_data.items():
                if df.empty or len(df) < 100:  # Need sufficient data
                    continue

                # Calculate various trend metrics
                prices = df['Close']
                returns = prices.pct_change(fill_method=None).dropna()

                # Basic statistics
                total_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
                annualized_return = ((prices.iloc[-1] / prices.iloc[0]) ** (252 / len(df)) - 1) * 100
                volatility = returns.std() * np.sqrt(252) * 100

                # Drawdown analysis
                cumulative = (1 + returns).cumprod()
                rolling_max = cumulative.expanding().max()
                drawdown = (cumulative - rolling_max) / rolling_max
                max_drawdown = drawdown.min() * 100

                # Trend strength (simple linear regression on log prices)
                log_prices = np.log(prices)
                x = np.arange(len(log_prices))
                slope, intercept = np.polyfit(x, log_prices, 1)
                trend_strength = slope * len(log_prices)  # Total log return

                trend_analysis[asset_class][ticker] = {
                    'total_return_pct': round(total_return, 2),
                    'annualized_return_pct': round(annualized_return, 2),
                    'volatility_pct': round(volatility, 2),
                    'max_drawdown_pct': round(max_drawdown, 2),
                    'trend_strength': round(trend_strength, 4),
                    'sharpe_ratio': round(annualized_return / volatility, 3) if volatility > 0 else 0,
                    'data_quality': 'high' if len(df) > 1000 else 'medium' if len(df) > 250 else 'low'
                }

        return trend_analysis
