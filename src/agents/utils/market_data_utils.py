"""
Market Data Utilities
Direct market data fetching functions without CrewAI agent overhead
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from . import fetch_market_data, get_supported_tickers


class MarketDataUtils:
    """Utility class for direct market data operations"""

    def __init__(self, output_dir: str = "src/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_data_direct(
        self,
        tickers: list[str] | None = None,
        period: str = "2y",
        include_analysis: bool = True
    ) -> dict[str, Any]:
        """
        Fetch market data directly without CrewAI agent

        Args:
            tickers: List of ticker symbols to fetch
            period: Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            include_analysis: Whether to include analysis summary

        Returns:
            Dictionary with fetch results and data summary
        """
        if tickers is None:
            # Get all tickers from the default set
            ticker_dict = get_supported_tickers()
            tickers = []
            for category_tickers in ticker_dict.values():
                tickers.extend(category_tickers)

        print(f"Fetching data for {len(tickers)} tickers over {period} period...")

        # Fetch data for all tickers
        ticker_data = fetch_market_data(tickers, period=period)
        successful_fetches = len(ticker_data)

        # Save individual ticker data
        for ticker, data in ticker_data.items():
            if data is not None and not data.empty:
                output_file = self.output_dir / f"{ticker.lower().replace('^', '')}_data.csv"
                data.to_csv(output_file)

        # Create summary report
        summary = self._create_data_summary(ticker_data)

        # Save summary
        summary_file = self.output_dir / "market_data_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        return {
            'successful_fetches': successful_fetches,
            'total_tickers': len(tickers),
            'data_summary': summary,
            'output_directory': str(self.output_dir)
        }

    def _create_data_summary(self, data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        """Create detailed summary of fetched market data with analysis"""
        summary: dict[str, Any] = {
            "fetch_timestamp": datetime.now().isoformat(),
            "tickers_processed": len(data),
            "tickers": {}
        }

        for ticker, df in data.items():
            if df.empty:
                summary["tickers"][ticker] = {"error": "No data available"}
                continue

            try:
                # Convert index to datetime if it's not already
                if not isinstance(df.index, pd.DatetimeIndex):
                    df = df.reset_index()
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                        df.set_index('Date', inplace=True)

                latest_price = df['Close'].iloc[-1]
                price_change = df['Close'].pct_change().iloc[-1]
                volatility = df['Close'].pct_change().std() * (252 ** 0.5)  # Annualized

                summary["tickers"][ticker] = {
                    "data_points": len(df),
                    "date_range": {
                        "start": df.index.min().isoformat() if hasattr(df.index.min(), 'isoformat') else str(df.index.min()),
                        "end": df.index.max().isoformat() if hasattr(df.index.max(), 'isoformat') else str(df.index.max())
                    },
                    "latest_price": float(latest_price),
                    "daily_change": float(price_change) if not pd.isna(price_change) else 0.0,
                    "annualized_volatility": float(volatility) if not pd.isna(volatility) else 0.0,
                    "price_range": {
                        "min": float(df['Close'].min()),
                        "max": float(df['Close'].max())
                    }
                }
            except Exception as e:
                summary["tickers"][ticker] = {"error": str(e)}

        return summary

    def get_latest_prices(self, tickers: list[str]) -> dict[str, float]:
        """Get latest prices for specified tickers"""
        prices = {}

        # Fetch data for all tickers at once
        try:
            data_dict = fetch_market_data(tickers, period="1d")
            for ticker, data in data_dict.items():
                if data is not None and not data.empty and 'Close' in data.columns:
                    prices[ticker] = float(data['Close'].iloc[-1])
                else:
                    prices[ticker] = 0.0
        except Exception as e:
            print(f"Failed to get prices: {e}")
            for ticker in tickers:
                prices[ticker] = 0.0

        return prices
