"""
Centralized constants for the AI Safety website.

Single source of truth for colors, display names, and ticker descriptions
used across plot_generator, icon_generator, and historical_visualization.
"""


# ---------------------------------------------------------------------------
# Website color scheme - cohesive blue theme with complementary accents
# ---------------------------------------------------------------------------

COLORS: dict[str, str] = {
    "primary_blue": "#0a1f44",
    "medium_blue": "#1e4a80",
    "accent_blue": "#295da0",
    "light_blue": "#4da3d8",
    "bright_blue": "#66c2ff",
    "soft_cyan": "#7dd3fc",
    "mint_green": "#10b981",
    "warm_amber": "#f59e0b",
    "soft_purple": "#8b5cf6",
    "coral_pink": "#f97316",
    "background": "#f5f8fc",
    "text_dark": "#2c3e50",
    "text_light": "#6a7aa2",
    "white": "#ffffff",
    "light_gray": "#e2e8f0",
}

# Ordered palette list used by seaborn and multi-series plots
PALETTE: list[str] = [
    COLORS["primary_blue"],
    COLORS["accent_blue"],
    COLORS["light_blue"],
    COLORS["bright_blue"],
    COLORS["soft_cyan"],
    COLORS["mint_green"],
    COLORS["warm_amber"],
    COLORS["soft_purple"],
    COLORS["coral_pink"],
]

# Per-category accent colors for plots
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
    "XRP-USD": "Ripple (XRP)",
    "XLM-USD": "Stellar (XLM)",
    "HBAR-USD": "Hedera (HBAR)",
    "ALGO-USD": "Algorand (ALGO)",
    "LINK-USD": "Chainlink (LINK)",
    "ONDO-USD": "Ondo Finance",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "SUI-USD": "Sui",
    "ADA-USD": "Cardano",
    "AVAX-USD": "Avalanche",
    "BTC-USD": "Bitcoin",
    "DOT-USD": "Polkadot",
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


# ---------------------------------------------------------------------------
# Shared plot styling (single source of truth for all modules)
# ---------------------------------------------------------------------------


def setup_plot_style() -> None:
    """Configure matplotlib for professional styling matching website theme.

    Called by plot_generator and historical_visualization before creating
    any chart.  Centralised here so there is exactly one place to update
    the visual language.
    """
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.edgecolor": COLORS["text_light"],
        "axes.linewidth": 1.2,
        "grid.color": "#e8f2fe",
        "grid.linestyle": "-",
        "grid.linewidth": 0.8,
        "grid.alpha": 0.7,
        "font.family": ["Arial", "Helvetica", "sans-serif"],
        "font.size": 12,
        "axes.titlesize": 16,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "text.color": COLORS["text_dark"],
        "axes.labelcolor": COLORS["text_dark"],
        "xtick.color": COLORS["text_light"],
        "ytick.color": COLORS["text_light"],
    })
