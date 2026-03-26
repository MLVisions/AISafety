"""
Data source utilities for market data and research
Provides standardized interfaces for fetching financial and economic data
"""

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]

# Comprehensive tickers for AI Safety investment analysis
DEFAULT_TICKERS = {
    'equity': [
        # Major Indices
        '^GSPC',    # S&P 500 Index
        '^DJI',     # Dow Jones Industrial Average
        '^IXIC',    # NASDAQ Composite
        '^RUT',     # Russell 2000
        # ETFs - Broad Market
        'SPY',      # SPDR S&P 500 ETF
        'QQQ',      # Invesco QQQ ETF (NASDAQ 100)
        'IWM',      # iShares Russell 2000 ETF
        'VTI',      # Vanguard Total Stock Market ETF
        # ETFs - Sector
        'XLP',      # Consumer Staples Select Sector SPDR
        'XLF',      # Financial Select Sector SPDR
        'XLK',      # Technology Select Sector SPDR
        'XLE',      # Energy Select Sector SPDR
        # Individual Stocks - AI/Tech Focus
        'AAPL',     # Apple Inc.
        'MSFT',     # Microsoft Corporation
        'GOOGL',    # Alphabet Inc.
        'AMZN',     # Amazon.com Inc.
        'NVDA',     # NVIDIA Corporation
        'TSLA',     # Tesla Inc.
        'META',     # Meta Platforms Inc.
    ],
    'international': [
        # International Indices
        '^FTSE',    # FTSE 100 (UK)
        '^N225',    # Nikkei 225 (Japan)
        '^HSI',     # Hang Seng Index (Hong Kong)
        '^GDAXI',   # DAX Performance Index (Germany)
        # International ETFs
        'VEA',      # Vanguard FTSE Developed Markets ETF
        'VWO',      # Vanguard FTSE Emerging Markets ETF
        'EFA',      # iShares MSCI EAFE ETF
        'EEM',      # iShares MSCI Emerging Markets ETF
    ],
    'crypto': [
        # Utility & payment tokens first
        'XRP-USD',  # Ripple (cross-border payments)
        'XLM-USD',  # Stellar (low-cost transactions)
        'HBAR-USD', # Hedera Hashgraph (enterprise DLT)
        'ALGO-USD', # Algorand (scalable dApps)
        'LINK-USD', # Chainlink (oracle network)
        'ONDO-USD', # Ondo Finance (tokenized real-world assets)
        # Platform & smart-contract tokens
        'ETH-USD',  # Ethereum
        'SOL-USD',  # Solana
        'SUI-USD',  # Sui
        'ADA-USD',  # Cardano
        'AVAX-USD', # Avalanche
        # Store-of-value
        'BTC-USD',  # Bitcoin
        'DOT-USD',  # Polkadot
    ],
    'commodities': [
        # Precious Metals
        'GC=F',     # Gold Futures
        'SI=F',     # Silver Futures
        'PL=F',     # Platinum Futures
        # Energy
        'CL=F',     # Crude Oil Futures
        'NG=F',     # Natural Gas Futures
        # Industrial Metals
        'HG=F',     # Copper Futures
        # Agricultural
        'ZC=F',     # Corn Futures
        'ZW=F',     # Wheat Futures
        # Commodity ETFs (for longer history)
        'GLD',      # SPDR Gold Shares
        'SLV',      # iShares Silver Trust
        'USO',      # United States Oil Fund
        'DBA',      # Invesco DB Agriculture Fund
    ],
    'real_estate': [
        # REITs and Real Estate
        'VNQ',      # Vanguard Real Estate ETF
        'IYR',      # iShares U.S. Real Estate ETF
        'RWR',      # SPDR Dow Jones REIT ETF
        'XLRE',     # Real Estate Select Sector SPDR Fund
        # Individual REITs
        'PLD',      # Prologis Inc. (Industrial)
        'AMT',      # American Tower Corp (Cell Towers)
        'CCI',      # Crown Castle International (Infrastructure)
        'SPG',      # Simon Property Group (Retail)
    ],
    'bonds': [
        # Treasury Yields
        '^TNX',     # 10-Year Treasury Note Yield
        '^TYX',     # 30-Year Treasury Bond Yield
        '^FVX',     # 5-Year Treasury Note Yield
        '^IRX',     # 3-Month Treasury Bill Yield
        # Bond ETFs
        'TLT',      # iShares 20+ Year Treasury Bond ETF
        'IEF',      # iShares 7-10 Year Treasury Bond ETF
        'SHY',      # iShares 1-3 Year Treasury Bond ETF
        'AGG',      # iShares Core U.S. Aggregate Bond ETF
        'HYG',      # iShares iBoxx $ High Yield Corporate Bond ETF
        'LQD',      # iShares iBoxx $ Investment Grade Corporate Bond ETF
    ]
}


def get_supported_tickers() -> dict[str, list[str]]:
    """
    Get dictionary of supported ticker symbols by category

    Returns:
        Dictionary with categories as keys and ticker lists as values
    """
    return DEFAULT_TICKERS.copy()


def fetch_market_data(
    tickers: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = "2y"
) -> dict[str, pd.DataFrame]:
    """
    Fetch historical market data for given tickers using yfinance

    Args:
        tickers: List of ticker symbols
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        period: Period to fetch if dates not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Dictionary mapping ticker symbols to DataFrames with OHLCV data
    """
    results = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            if start_date and end_date:
                data = stock.history(start=start_date, end=end_date)
            else:
                data = stock.history(period=period)

            if not data.empty:
                # Clean up the data
                data = data.reset_index()
                data.columns = [col.title() if col != 'Date' else col for col in data.columns]
                # Convert timezone-aware datetime to timezone-naive to avoid matplotlib issues
                if 'Date' in data.columns and pd.api.types.is_datetime64_any_dtype(data['Date']):
                    data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
                results[ticker] = data
            else:
                print(f"Warning: No data found for ticker {ticker}")

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

    return results


def get_ticker_info(ticker: str) -> dict[str, Any] | None:
    """
    Get detailed information about a ticker symbol

    Args:
        ticker: Ticker symbol

    Returns:
        Dictionary with ticker information or None if not found
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info if isinstance(info, dict) else None
    except Exception as e:
        print(f"Error getting info for {ticker}: {e}")
        return None


def calculate_returns(data: pd.DataFrame, column: str = 'Close') -> pd.DataFrame:
    """
    Calculate various return metrics for price data

    Args:
        data: DataFrame with price data
        column: Column name to calculate returns from

    Returns:
        DataFrame with additional return columns
    """
    df = data.copy()

    # Simple returns
    df['Daily_Return'] = df[column].pct_change()
    df['Weekly_Return'] = df[column].pct_change(periods=7)
    df['Monthly_Return'] = df[column].pct_change(periods=30)

    # Cumulative returns
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1

    # Moving averages
    df['MA_20'] = df[column].rolling(window=20).mean()
    df['MA_50'] = df[column].rolling(window=50).mean()
    df['MA_200'] = df[column].rolling(window=200).mean()

    return df


def get_recent_data(
    tickers: list[str],
    days: int = 30
) -> dict[str, pd.DataFrame]:
    """
    Get recent market data for analysis

    Args:
        tickers: List of ticker symbols
        days: Number of recent days to fetch

    Returns:
        Dictionary mapping tickers to recent data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    return fetch_market_data(
        tickers,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )


def fetch_maximum_history(ticker: str) -> pd.DataFrame | None:
    """
    Fetch maximum available historical data for a ticker

    Args:
        ticker: Ticker symbol

    Returns:
        DataFrame with maximum historical data or None if failed
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="max")

        if not data.empty:
            data = data.reset_index()
            data.columns = [col.title() if col != 'Date' else col for col in data.columns]
            # Convert timezone-aware datetime to timezone-naive to avoid matplotlib issues
            if 'Date' in data.columns and pd.api.types.is_datetime64_any_dtype(data['Date']):
                data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            return data
        else:
            print(f"Warning: No data found for ticker {ticker}")
            return None

    except Exception as e:
        print(f"Error fetching maximum history for {ticker}: {e}")
        return None


def get_asset_class_data(asset_class: str, max_history: bool = False) -> dict[str, pd.DataFrame]:
    """
    Get all tickers for a specific asset class

    Args:
        asset_class: One of 'equity', 'international', 'crypto', 'commodities', 'real_estate', 'bonds'
        max_history: Whether to fetch maximum available history

    Returns:
        Dictionary mapping tickers to their data
    """
    if asset_class not in DEFAULT_TICKERS:
        raise ValueError(f"Unknown asset class: {asset_class}")

    tickers = DEFAULT_TICKERS[asset_class]

    if max_history:
        results = {}
        for ticker in tickers:
            data = fetch_maximum_history(ticker)
            if data is not None:
                results[ticker] = data
        return results
    else:
        return fetch_market_data(tickers)


def get_all_asset_data(max_history: bool = False) -> dict[str, dict[str, pd.DataFrame]]:
    """
    Get data for all asset classes

    Args:
        max_history: Whether to fetch maximum available history

    Returns:
        Nested dictionary: asset_class -> ticker -> DataFrame
    """
    all_data = {}

    for asset_class in DEFAULT_TICKERS.keys():
        print(f"Fetching {asset_class} data...")
        all_data[asset_class] = get_asset_class_data(asset_class, max_history)

    return all_data


def analyze_data_availability(ticker: str) -> dict[str, Any]:
    """
    Analyze data availability and date range for a ticker

    Args:
        ticker: Ticker symbol

    Returns:
        Dictionary with data availability information
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="max")

        if data.empty:
            return {"ticker": ticker, "available": False, "error": "No data found"}

        start_date = data.index.min()
        end_date = data.index.max()
        total_days = (end_date - start_date).days
        data_points = len(data)

        return {
            "ticker": ticker,
            "available": True,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "total_days": total_days,
            "total_years": round(total_days / 365.25, 2),
            "data_points": data_points,
            "frequency": "daily" if data_points > total_days * 0.8 else "irregular"
        }

    except Exception as e:
        return {"ticker": ticker, "available": False, "error": str(e)}


def get_all_data_availability() -> pd.DataFrame:
    """
    Get data availability analysis for all tickers

    Returns:
        DataFrame with availability information for all tickers
    """
    all_info = []

    for asset_class, tickers in DEFAULT_TICKERS.items():
        for ticker in tickers:
            info = analyze_data_availability(ticker)
            info["asset_class"] = asset_class
            all_info.append(info)

    return pd.DataFrame(all_info)
