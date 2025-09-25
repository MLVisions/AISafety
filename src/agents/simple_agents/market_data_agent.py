"""
Market Data Agent - Simple Agent for fetching financial market data
Uses yfinance and other APIs to gather pricing and economic data
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from crewai import Agent, Task
from crewai_tools import DirectoryReadTool, FileReadTool

from ..utils import fetch_market_data, get_supported_tickers


class MarketDataAgent:
    """Agent responsible for fetching and managing market data"""

    def __init__(self, output_dir: str = "src/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize CrewAI agent
        self.agent = Agent(
            role="Market Data Analyst",
            goal=(
                "Fetch accurate, up-to-date market data for stocks, cryptocurrencies, "
                "and other financial instruments. Provide clean, structured data for "
                "analysis and plot generation."
            ),
            backstory=(
                "You are an experienced financial data analyst with expertise in "
                "market data APIs, data cleaning, and financial analysis. You ensure "
                "data quality and handle API limitations gracefully."
            ),
            tools=[FileReadTool(), DirectoryReadTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )

    def create_fetch_task(
        self,
        tickers: list[str] | None = None,
        period: str = "2y",
        include_analysis: bool = True
    ) -> Task:
        """
        Create a task to fetch market data

        Args:
            tickers: List of ticker symbols to fetch (uses defaults if None)
            period: Time period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            include_analysis: Whether to include basic analysis metrics

        Returns:
            CrewAI Task for data fetching
        """
        if tickers is None:
            supported = get_supported_tickers()
            tickers = supported['equity'] + supported['crypto'][:2]  # Limit crypto for performance

        description = f"""
        Fetch historical market data for the following tickers: {', '.join(tickers)}

        Requirements:
        1. Fetch {period} of historical data for each ticker
        2. Clean and validate the data (remove missing values, check for anomalies)
        3. Save individual CSV files for each ticker in {self.output_dir}
        4. Create a summary report with data statistics
        """

        if include_analysis:
            description += """
        5. Calculate basic metrics: daily returns, volatility, moving averages
        6. Generate a market summary with key insights
            """

        description += f"""

        Output files should be saved as:
        - Individual ticker data: {self.output_dir}/{{ticker}}_historical.csv
        - Market summary: {self.output_dir}/market_summary.json

        Use the fetch_market_data utility function and ensure all data is properly formatted.
        """

        return Task(
            description=description,
            agent=self.agent,
            expected_output=(
                "CSV files with clean historical data for each ticker, "
                "plus a JSON summary with market statistics and insights."
            )
        )

    def fetch_data_direct(
        self,
        tickers: list[str] | None = None,
        period: str = "2y"
    ) -> dict[str, pd.DataFrame]:
        """
        Direct method to fetch market data without CrewAI task orchestration
        Useful for simple data fetching needs

        Args:
            tickers: List of ticker symbols
            period: Time period to fetch

        Returns:
            Dictionary mapping tickers to DataFrames
        """
        if tickers is None:
            supported = get_supported_tickers()
            tickers = supported['equity'] + supported['crypto']

        print(f"📊 Fetching market data for {len(tickers)} tickers...")

        # Fetch data using utility function
        data = fetch_market_data(tickers, period=period)

        # Save to CSV files
        for ticker, df in data.items():
            if not df.empty:
                output_file = self.output_dir / f"{ticker.replace('/', '_')}_historical.csv"
                df.to_csv(output_file, index=False)
                print(f"   ✅ Saved {ticker} data to {output_file}")

        # Create summary
        summary = self._create_data_summary(data)
        summary_file = self.output_dir / "market_summary.json"

        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"📈 Market data fetch complete. {len(data)} tickers processed.")
        return data

    def _create_data_summary(self, data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        """Create a summary of fetched market data"""
        summary: dict[str, Any] = {
            "fetch_timestamp": datetime.now().isoformat(),
            "tickers_processed": len(data),
            "tickers": {}
        }

        for ticker, df in data.items():
            if df.empty:
                continue

            try:
                latest_price = df['Close'].iloc[-1]
                price_change = df['Close'].pct_change().iloc[-1]
                volatility = df['Close'].pct_change().std() * (252 ** 0.5)  # Annualized

                summary["tickers"][ticker] = {
                    "data_points": len(df),
                    "date_range": {
                        "start": df['Date'].min(),
                        "end": df['Date'].max()
                    },
                    "latest_price": latest_price,
                    "daily_change": price_change,
                    "annualized_volatility": volatility,
                    "price_range": {
                        "min": df['Close'].min(),
                        "max": df['Close'].max()
                    }
                }
            except Exception as e:
                summary["tickers"][ticker] = {"error": str(e)}

        return summary

    def get_latest_prices(self, tickers: list[str]) -> dict[str, float]:
        """
        Get latest prices for given tickers

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping tickers to latest prices
        """
        data = fetch_market_data(tickers, period="5d")
        prices = {}

        for ticker, df in data.items():
            if not df.empty:
                prices[ticker] = df['Close'].iloc[-1]

        return prices


def create_market_data_agent(output_dir: str = "src/data") -> MarketDataAgent:
    """Factory function to create a MarketDataAgent"""
    return MarketDataAgent(output_dir=output_dir)


if __name__ == "__main__":
    # Test the agent
    agent = create_market_data_agent()

    # Test direct data fetching
    test_tickers = ['^GSPC', 'BTC-USD', 'AAPL']
    data = agent.fetch_data_direct(test_tickers, period="1mo")

    print(f"Fetched data for {len(data)} tickers")
    for ticker, df in data.items():
        print(f"  {ticker}: {len(df)} data points")
