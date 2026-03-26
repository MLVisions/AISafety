"""
AI Safety Website Plot Generator.

Generates site-level data plots (market trends) from CSV files in src/data/.
Market-specific plots (raw tickers, category comparisons) live in
``src.market.plot_functions``.
"""

import matplotlib

matplotlib.use("Agg")

import os  # noqa: E402

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from agents.utils.constants import COLORS, PALETTE, setup_plot_style  # noqa: E402

sns.set_palette(PALETTE)

def create_market_trends_plot(
    csv_path: str = "data/market_trends.csv",
    save_path: str = "images/market_trends.png",
) -> None:
    """Create S&P 500 and Bitcoin market trends plot."""
    setup_plot_style()

    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])

    # Create figure with dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')

    # Plot S&P 500
    color1 = COLORS['primary_blue']
    ax1.plot(df['Date'], df['SP500'], color=color1, linewidth=3, label='S&P 500', marker='o', markersize=6)
    ax1.set_xlabel('Year', fontweight='bold', color=COLORS['text_dark'])
    ax1.set_ylabel('S&P 500 Index', fontweight='bold', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    # Create second y-axis for Bitcoin
    ax2 = ax1.twinx()
    color2 = COLORS['warm_amber']
    ax2.plot(df['Date'], df['Bitcoin'], color=color2, linewidth=3, label='Bitcoin', marker='s', markersize=6)
    ax2.set_ylabel('Bitcoin Price (USD)', fontweight='bold', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    # Format dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # Add title and legend
    plt.title('S&P 500 and Bitcoin Market Trends (2020-2025)',
              fontsize=18, fontweight='bold', color=COLORS['text_dark'], pad=20)

    # Create custom legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Close the figure to free memory

def generate_all_plots(data_dir: str = "data", output_dir: str = "images") -> None:
    """Generate all site-level plots from CSV data."""
    os.makedirs(output_dir, exist_ok=True)

    create_market_trends_plot(
        csv_path=f"{data_dir}/market_trends.csv",
        save_path=f"{output_dir}/market_trends.png",
    )

    print("  Generated 1 data plot.")
