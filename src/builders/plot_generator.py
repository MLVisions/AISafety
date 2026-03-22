"""
AI Safety Website Plot Generator
Professional plotting functions that match the website's design theme
"""

import matplotlib

matplotlib.use('Agg')  # Use non-interactive backend to prevent popups
import os
from datetime import datetime
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

from src.agents.utils.constants import (
    ASSET_COLORS,
    CATEGORY_COLORS,
    CATEGORY_PALETTE,
    COLORS,
    PALETTE,
    get_category_description,
    get_ticker_description,
    get_ticker_display_name,
    setup_plot_style,
)

# Set the seaborn palette with cohesive theme colors
sns.set_palette(PALETTE)

def create_market_trends_plot(csv_path: str = 'data/market_trends.csv', save_path: str = 'website/images/market_trends_new.png') -> None:
    """Create S&P 500 and Bitcoin market trends plot"""
    setup_plot_style()

    # Load data
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])

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

def create_portfolio_projection_plot(person: str = 'A', csv_path: str | None = None, save_path: str | None = None) -> None:
    """Create individual portfolio projection plot"""
    setup_plot_style()

    if csv_path is None:
        csv_path = f'data/person{person}_portfolio.csv'
    if save_path is None:
        save_path = f'website/images/person{person}_new.png'

    # Load data
    df = pd.read_csv(csv_path)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')

    # Define colors for different asset types from centralized constants
    colors = ASSET_COLORS

    # Create stacked area plot for asset allocation
    bottom = np.zeros(len(df))

    # Get asset columns (exclude Year, Total, bounds)
    asset_cols = [col for col in df.columns if col.startswith(f'Person{person}') and
                  col not in [f'Person{person}_Total', f'Person{person}_Lower', f'Person{person}_Upper']]

    for col in asset_cols:
        if col in df.columns:
            asset_name = col.split('_')[1]  # Extract asset type
            color = colors.get(asset_name, COLORS['light_gray'])
            ax.fill_between(df['Year'], bottom, bottom + df[col],
                          color=color, alpha=0.7, label=asset_name)
            bottom += df[col]

    # Add uncertainty bands if available
    if f'Person{person}_Lower' in df.columns and f'Person{person}_Upper' in df.columns:
        ax.fill_between(df['Year'], df[f'Person{person}_Lower'], df[f'Person{person}_Upper'],
                       color=COLORS['primary_blue'], alpha=0.2, label='Uncertainty Range')

    # Add total line
    if f'Person{person}_Total' in df.columns:
        ax.plot(df['Year'], df[f'Person{person}_Total'],
               color=COLORS['primary_blue'], linewidth=3, marker='o', markersize=8,
               label='Total Portfolio Value')

    # Formatting
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('Portfolio Value (2025 dollars)', fontweight='bold')
    ax.set_title(f'Portfolio Projection: Person {person}',
                fontsize=18, fontweight='bold', color=COLORS['text_dark'], pad=20)

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Legend
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, framealpha=0.9)

    # Grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Close the figure to free memory

def create_comparative_wealth_plot(data_dir: str = 'data', save_path: str = 'website/images/comparative_wealth.png') -> None:
    """Create comparative wealth outcomes bar chart using actual portfolio data"""
    setup_plot_style()

    # Load individual portfolio data
    person_a_df = pd.read_csv(f'{data_dir}/personA_portfolio.csv')
    person_b_df = pd.read_csv(f'{data_dir}/personB_portfolio.csv')
    person_c_df = pd.read_csv(f'{data_dir}/personC_portfolio.csv')

    # Extract 2030 data for each person
    a_2030 = person_a_df[person_a_df['Year'] == 2030].iloc[0]
    b_2030 = person_b_df[person_b_df['Year'] == 2030].iloc[0]
    c_2030 = person_c_df[person_c_df['Year'] == 2030].iloc[0]

    # Prepare comparison data
    persons = ['Person A', 'Person B', 'Person C']
    portfolios = [a_2030['PersonA_Total'], b_2030['PersonB_Total'], c_2030['PersonC_Total']]
    lower_bounds = [a_2030['PersonA_Lower'], b_2030['PersonB_Lower'], c_2030['PersonC_Lower']]
    upper_bounds = [a_2030['PersonA_Upper'], b_2030['PersonB_Upper'], c_2030['PersonC_Upper']]

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')

    # Create bar chart with cohesive theme colors
    x_pos = np.arange(len(persons))
    bars = ax.bar(x_pos, portfolios,
                  color=[COLORS['primary_blue'], COLORS['light_blue'], COLORS['mint_green']],
                  alpha=0.85, width=0.6)

    # Add error bars for uncertainty
    error_lower = [portfolios[i] - lower_bounds[i] for i in range(len(portfolios))]
    error_upper = [upper_bounds[i] - portfolios[i] for i in range(len(portfolios))]
    ax.errorbar(x_pos, portfolios,
               yerr=[error_lower, error_upper],
               fmt='none', color='black', capsize=8, capthick=2, linewidth=2)

    # Formatting
    ax.set_xlabel('Investment Strategy', fontweight='bold')
    ax.set_ylabel('Total Wealth in 2030 (2025 dollars)', fontweight='bold')
    ax.set_title('Comparative Wealth Accumulation (2025-2030) with Variability',
                fontsize=18, fontweight='bold', color=COLORS['text_dark'], pad=20)

    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(persons)

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    # Add value labels on bars
    for _, (bar, value) in enumerate(zip(bars, portfolios, strict=False)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
               f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')

    # Add strategy descriptions as subtitle text
    strategies = [
        'Conservative (Savings + 401k)',
        'Balanced (Tech + Real Estate + Savings + 401k)',
        'Aggressive (Crypto + Tech + Savings + House + 401k)'
    ]

    for _, (bar, strategy) in enumerate(zip(bars, strategies, strict=False)):
        ax.text(bar.get_x() + bar.get_width()/2, -15000,
               strategy, ha='center', va='top', fontsize=9,
               style='italic', color=COLORS['text_light'])

    # Grid
    ax.grid(True, alpha=0.3, axis='y')

    # Adjust layout to make room for strategy labels
    plt.subplots_adjust(bottom=0.15)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Close the figure to free memory

def generate_all_plots(data_dir: str = 'data', output_dir: str = 'images') -> None:
    """Generate all plots and save them"""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    create_market_trends_plot(
        csv_path=f'{data_dir}/market_trends.csv',
        save_path=f'{output_dir}/market_trends.png'
    )

    for person in ['A', 'B', 'C']:
        create_portfolio_projection_plot(
            person=person,
            csv_path=f'{data_dir}/person{person}_portfolio.csv',
            save_path=f'{output_dir}/person{person}.png'
        )

    create_comparative_wealth_plot(
        data_dir=data_dir,
        save_path=f'{output_dir}/comparative_wealth.png'
    )

    print("  Generated 5 data plots.")


def create_raw_ticker_plots(output_dir: str = 'src/static/images/raw_tickers') -> None:
    """
    Create individual plots for all raw ticker data and save them for website integration
    """
    from ..agents.utils.data_sources import DEFAULT_TICKERS, fetch_maximum_history

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    setup_plot_style()

    total_created = 0

    for category, tickers in DEFAULT_TICKERS.items():

        for ticker_symbol in tickers:
            try:
                # Fetch maximum available historical data
                data = fetch_maximum_history(ticker_symbol)

                if data is None or data.empty:
                    continue

                # Create plot
                fig, ax = plt.subplots(figsize=(12, 8))
                fig.patch.set_facecolor('white')

                # Plot closing price over time
                ax.plot(data['Date'], data['Close'],
                       color=CATEGORY_COLORS[category], linewidth=2, alpha=0.8)

                # Add moving averages for context
                if len(data) > 50:
                    ma_50 = data['Close'].rolling(window=50).mean()
                    ax.plot(data['Date'], ma_50,
                           color=COLORS['light_gray'], linewidth=1, alpha=0.7,
                           linestyle='--', label='50-day MA')

                if len(data) > 200:
                    ma_200 = data['Close'].rolling(window=200).mean()
                    ax.plot(data['Date'], ma_200,
                           color=COLORS['text_light'], linewidth=1, alpha=0.7,
                           linestyle=':', label='200-day MA')

                # Formatting
                clean_ticker = ticker_symbol.replace('^', '').replace('-USD', '').replace('=F', '')
                ax.set_title(f'{clean_ticker} - Historical Price Data ({category.title()})',
                           fontsize=16, fontweight='bold', color=COLORS['text_dark'], pad=20)

                ax.set_xlabel('Date', fontweight='bold')
                ax.set_ylabel('Price ($)', fontweight='bold')

                # Format dates on x-axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
                ax.xaxis.set_major_locator(mdates.YearLocator(base=max(1, len(data) // (252 * 5))))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

                # Grid and legend
                ax.grid(True, alpha=0.3)
                if len(data) > 200:
                    ax.legend(frameon=True, fancybox=True, shadow=True, framealpha=0.9)

                # Add data range info
                start_date = data['Date'].iloc[0].strftime('%Y-%m-%d')
                end_date = data['Date'].iloc[-1].strftime('%Y-%m-%d')
                data_range = f"Data: {start_date} to {end_date} ({len(data)} days)"
                ax.text(0.02, 0.98, data_range, transform=ax.transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': 0.8})

                # Save plot
                safe_filename = ticker_symbol.replace('^', 'INDEX_').replace('-', '_').replace('=', '_')
                save_path = os.path.join(output_dir, f'{safe_filename}_historical.png')

                plt.tight_layout()
                plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()

                total_created += 1

            except Exception as e:
                print(f"  Warning: No data for {ticker_symbol}: {e}")
                continue

    print(f"  Generated {total_created} raw ticker plots.")


def create_category_comparison_plots(output_dir: str = 'src/static/images/category_comparisons') -> None:
    """
    Create comparison plots showing multiple tickers from each category
    """
    from ..agents.utils.data_sources import DEFAULT_TICKERS, fetch_maximum_history

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    setup_plot_style()

    total_created = 0

    for category, tickers in DEFAULT_TICKERS.items():
        # Take first 3-5 tickers for comparison to avoid clutter
        comparison_tickers = tickers[:min(5, len(tickers))]

        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')

        colors = CATEGORY_PALETTE[category]
        successful_plots = 0

        for i, ticker_sym in enumerate(comparison_tickers):
            try:
                data = fetch_maximum_history(ticker_sym)

                if data is None or data.empty:
                    continue

                # Normalize to starting value for comparison
                normalized = (data['Close'] / data['Close'].iloc[0]) * 100

                color = colors[i % len(colors)]
                clean_name = ticker_sym.replace('^', '').replace('-USD', '').replace('=F', '')

                ax.plot(data['Date'], normalized.values,
                       color=color, linewidth=2, alpha=0.8, label=clean_name)

                successful_plots += 1

            except Exception as e:
                print(f"Error plotting {ticker_sym} in category comparison: {e}")
                continue

        if successful_plots > 0:
            # Formatting
            ax.set_title(f'{category.title()} Assets - Normalized Performance Comparison',
                       fontsize=18, fontweight='bold', color=COLORS['text_dark'], pad=20)

            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Normalized Price (Starting Value = 100)', fontweight='bold')

            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            # Grid and legend
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, framealpha=0.9)

            # Horizontal line at 100 for reference
            ax.axhline(y=100, color=COLORS['text_light'], linestyle='--', alpha=0.5)

            # Save
            save_path = os.path.join(output_dir, f'{category}_comparison.png')
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            total_created += 1

        else:
            plt.close()

    print(f"  Generated {total_created} category comparison plots.")


def create_ticker_dropdown_data(output_file: str = 'src/static/data/ticker_dropdown.json') -> dict:
    """
    Create JSON data structure for ticker dropdown functionality
    """
    import json

    from ..agents.utils.data_sources import DEFAULT_TICKERS

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    dropdown_data: dict[str, Any] = {
        "categories": {},
        "metadata": {
            "total_tickers": 0,
            "generated_at": datetime.now().isoformat(),
            "description": "Raw ticker historical data for portfolio analysis evidence"
        }
    }

    total_count = 0

    for category, tickers in DEFAULT_TICKERS.items():
        dropdown_data["categories"][category] = {
            "display_name": category.replace('_', ' ').title(),
            "description": get_category_description(category),
            "tickers": []
        }

        for ticker_name in tickers:
            # Create safe filename for lookup
            safe_filename = ticker_name.replace('^', 'INDEX_').replace('-', '_').replace('=', '_')

            ticker_info = {
                "ticker": ticker_name,
                "display_name": get_ticker_display_name(ticker_name),
                "image_path": f"images/raw_tickers/{safe_filename}_historical.png",
                "description": get_ticker_description(ticker_name)            }

            dropdown_data["categories"][category]["tickers"].append(ticker_info)
            total_count += 1

    dropdown_data["metadata"]["total_tickers"] = total_count

    # Save JSON file
    with open(output_file, 'w') as f:
        json.dump(dropdown_data, f, indent=2)

    print(f"  Created ticker dropdown data: {os.path.basename(output_file)}")
    return dropdown_data


if __name__ == "__main__":
    generate_all_plots()
