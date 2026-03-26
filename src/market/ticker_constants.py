"""
Ticker and category constants for market data.

Single source of truth for ticker display names, descriptions,
category metadata, and asset colors used by market visualizations,
plot generation, and the investment pipeline.
"""

from agents.utils.constants import COLORS

# ---------------------------------------------------------------------------
# Ticker display names - human-readable labels
# ---------------------------------------------------------------------------

TICKER_DISPLAY_NAMES: dict[str, str] = {
    # Equity indices
    "^GSPC": "S&P 500 Index",
    "^DJI": "Dow Jones",
    "^IXIC": "NASDAQ",
    "^RUT": "Russell 2000",
    # Equity ETFs
    "SPY": "S&P 500 ETF",
    "QQQ": "NASDAQ 100 ETF",
    "IWM": "Russell 2000 ETF",
    "VTI": "Total Stock Market ETF",
    "XLP": "Consumer Staples ETF",
    "XLF": "Financial Select ETF",
    "XLK": "Technology Select ETF",
    "XLE": "Energy Select ETF",
    # Individual stocks
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet/Google",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "TSLA": "Tesla",
    "META": "Meta/Facebook",
    # Crypto - utility and payment tokens first
    "XRP-USD": "XRP",
    "XLM-USD": "Stellar (XLM)",
    "HBAR-USD": "Hedera (HBAR)",
    "ALGO-USD": "Algorand (ALGO)",
    "LINK-USD": "Chainlink (LINK)",
    "ONDO-USD": "Ondo (ONDO)",
    "ETH-USD": "Ethereum (ETH)",
    "SOL-USD": "Solana (SOL)",
    "SUI-USD": "Sui (SUI)",
    "ADA-USD": "Cardano (ADA)",
    "AVAX-USD": "Avalanche (AVAX)",
    "BTC-USD": "Bitcoin (BTC)",
    "DOT-USD": "Polkadot (DOT)",
    # International indices
    "^FTSE": "FTSE 100 (UK)",
    "^N225": "Nikkei 225 (Japan)",
    "^HSI": "Hang Seng (HK)",
    "^GDAXI": "DAX (Germany)",
    # International ETFs
    "VEA": "Developed Markets ETF",
    "VWO": "Emerging Markets ETF",
    "EFA": "MSCI EAFE ETF",
    "EEM": "Emerging Markets ETF (iShares)",
    # Commodities
    "GC=F": "Gold Futures",
    "SI=F": "Silver Futures",
    "PL=F": "Platinum Futures",
    "CL=F": "Crude Oil",
    "NG=F": "Natural Gas",
    "HG=F": "Copper Futures",
    "ZC=F": "Corn Futures",
    "ZW=F": "Wheat Futures",
    "GLD": "Gold ETF",
    "SLV": "Silver ETF",
    "USO": "US Oil Fund",
    "DBA": "Agriculture Fund",
    # Real estate
    "VNQ": "Real Estate ETF",
    "IYR": "US Real Estate ETF",
    "RWR": "Dow Jones REIT ETF",
    "XLRE": "Real Estate Select ETF",
    "PLD": "Prologis (Industrial)",
    "AMT": "American Tower",
    "CCI": "Crown Castle",
    "SPG": "Simon Property Group",
    # Bonds
    "^TNX": "10-Year Treasury",
    "^TYX": "30-Year Treasury",
    "^FVX": "5-Year Treasury",
    "^IRX": "3-Month T-Bill",
    "TLT": "Long-Term Treasury ETF",
    "IEF": "7-10 Year Treasury ETF",
    "SHY": "1-3 Year Treasury ETF",
    "AGG": "Aggregate Bond ETF",
    "HYG": "High Yield Bond ETF",
    "LQD": "Investment Grade Bond ETF",
}


def get_ticker_display_name(ticker: str) -> str:
    """Return a human-readable name for *ticker*, falling back to the symbol."""
    return TICKER_DISPLAY_NAMES.get(ticker, ticker)


# ---------------------------------------------------------------------------
# Ticker descriptions
# ---------------------------------------------------------------------------

TICKER_DESCRIPTIONS: dict[str, str] = {
    "^GSPC": "Broad US market index tracking 500 largest companies",
    "^DJI": "Price-weighted index of 30 major US companies",
    "^IXIC": "Composite index of NASDAQ-listed securities",
    "BTC-USD": "Leading cryptocurrency and digital store of value",
    "XRP-USD": "Utility token for cross-border payments via Ripple network",
    "XLM-USD": "Stellar network token for low-cost cross-border transactions",
    "HBAR-USD": "Hedera Hashgraph utility token for enterprise DLT",
    "ALGO-USD": "Algorand blockchain token for scalable decentralized apps",
    "LINK-USD": "Decentralized oracle network connecting smart contracts to real-world data",
    "ONDO-USD": "Tokenized real-world asset protocol bridging DeFi and traditional finance",
    "ETH-USD": "Programmable blockchain platform for smart contracts and DeFi",
    "SOL-USD": "High-throughput blockchain for decentralized applications",
    "GC=F": "Precious metal commodity futures for inflation hedge",
    "VNQ": "Real estate investment trust ETF for property exposure",
    "^TNX": "US government 10-year bond yield indicator",
    "GLD": "Physical gold-backed ETF for inflation protection",
    "AGG": "Broad US bond market exposure across investment-grade fixed income",
}


def get_ticker_description(ticker: str) -> str:
    """Return a short description for *ticker*."""
    return TICKER_DESCRIPTIONS.get(
        ticker,
        f"Historical price data for {get_ticker_display_name(ticker)}",
    )


# ---------------------------------------------------------------------------
# Category descriptions
# ---------------------------------------------------------------------------

CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "equity": "US stocks, indices, and equity ETFs for domestic market exposure",
    "international": "Global markets and international equity exposure",
    "crypto": "Digital assets, utility tokens, and cryptocurrency investments",
    "commodities": "Raw materials, precious metals, energy, and agricultural products",
    "real_estate": "REITs and real estate investment trusts",
    "bonds": "Fixed income securities, treasury bonds, and bond ETFs",
}


def get_category_description(category: str) -> str:
    """Return a human-readable description for an asset *category*."""
    return CATEGORY_DESCRIPTIONS.get(category, f"{category.title()} investments")


# ---------------------------------------------------------------------------
# Per-category accent colors for plots
# ---------------------------------------------------------------------------

CATEGORY_COLORS: dict[str, str] = {
    "equity": COLORS["primary_blue"],
    "international": COLORS["accent_blue"],
    "crypto": COLORS["warm_amber"],
    "commodities": COLORS["mint_green"],
    "real_estate": COLORS["coral_pink"],
    "bonds": COLORS["soft_purple"],
}

# Multi-color list per category (for comparison charts with several series)
CATEGORY_PALETTE: dict[str, list[str]] = {
    "equity": [COLORS["primary_blue"], COLORS["medium_blue"], COLORS["accent_blue"]],
    "international": [COLORS["light_blue"], COLORS["bright_blue"], COLORS["soft_cyan"]],
    "crypto": [COLORS["warm_amber"], COLORS["coral_pink"], COLORS["soft_purple"]],
    "commodities": [COLORS["mint_green"], COLORS["accent_blue"], COLORS["light_blue"]],
    "real_estate": [COLORS["coral_pink"], COLORS["warm_amber"], COLORS["soft_purple"]],
    "bonds": [COLORS["soft_purple"], COLORS["medium_blue"], COLORS["accent_blue"]],
}

# ---------------------------------------------------------------------------
# Asset colors for portfolio plots
# ---------------------------------------------------------------------------

ASSET_COLORS: dict[str, str] = {
    "Savings": COLORS["light_blue"],
    "401k": COLORS["accent_blue"],
    "TechStocks": COLORS["soft_cyan"],
    "RealEstate": COLORS["mint_green"],
    "Crypto": COLORS["warm_amber"],
    "House": COLORS["coral_pink"],
}
