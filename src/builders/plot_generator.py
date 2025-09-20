"""
AI Safety Website Plot Generator
Professional plotting functions that match the website's design theme
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent popups
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import os

# Website color scheme
COLORS = {
    'primary_blue': '#0a1f44',
    'medium_blue': '#1e4a80', 
    'accent_blue': '#295da0',
    'light_blue': '#4da3d8',
    'bright_blue': '#66c2ff',
    'background': '#f5f8fc',
    'text_dark': '#2c3e50',
    'text_light': '#6a7aa2',
    'success_green': '#27ae60',
    'warning_orange': '#f39c12',
    'error_red': '#e74c3c',
    'neutral_gray': '#95a5a6'
}

# Set the style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette([COLORS['primary_blue'], COLORS['accent_blue'], COLORS['light_blue'], 
                COLORS['bright_blue'], COLORS['success_green'], COLORS['warning_orange']])

def setup_plot_style():
    """Configure matplotlib for professional styling matching website theme"""
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.edgecolor': COLORS['text_light'],
        'axes.linewidth': 1.2,
        'grid.color': '#e8f2fe',
        'grid.linestyle': '-',
        'grid.linewidth': 0.8,
        'grid.alpha': 0.7,
        'font.family': ['Arial', 'Helvetica', 'sans-serif'],
        'font.size': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 13,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11,
        'text.color': COLORS['text_dark'],
        'axes.labelcolor': COLORS['text_dark'],
        'xtick.color': COLORS['text_light'],
        'ytick.color': COLORS['text_light']
    })

def create_market_trends_plot(csv_path='data/market_trends.csv', save_path='website/images/market_trends_new.png'):
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
    color2 = COLORS['warning_orange']
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
    
    return fig

def create_portfolio_projection_plot(person='A', csv_path=None, save_path=None):
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
    
    # Define colors for different asset types
    colors = {
        'Savings': COLORS['light_blue'],
        '401k': COLORS['accent_blue'],
        'TechStocks': COLORS['success_green'],
        'RealEstate': COLORS['warning_orange'],
        'Crypto': COLORS['bright_blue'],
        'House': COLORS['error_red']
    }
    
    # Create stacked area plot for asset allocation
    bottom = np.zeros(len(df))
    
    # Get asset columns (exclude Year, Total, bounds)
    asset_cols = [col for col in df.columns if col.startswith(f'Person{person}') and 
                  col not in [f'Person{person}_Total', f'Person{person}_Lower', f'Person{person}_Upper']]
    
    for col in asset_cols:
        if col in df.columns:
            asset_name = col.split('_')[1]  # Extract asset type
            color = colors.get(asset_name, COLORS['neutral_gray'])
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
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Legend
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, framealpha=0.9)
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Close the figure to free memory
    
    return fig

def create_comparative_wealth_plot(csv_path='data/comparative_wealth.csv', save_path='website/images/comparative_wealth_new.png'):
    """Create comparative wealth outcomes bar chart"""
    setup_plot_style()
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')
    
    # Create bar chart
    x_pos = np.arange(len(df))
    bars = ax.bar(x_pos, df['Portfolio_2030'], 
                  color=[COLORS['primary_blue'], COLORS['accent_blue'], COLORS['success_green']], 
                  alpha=0.8, width=0.6)
    
    # Add error bars for uncertainty
    ax.errorbar(x_pos, df['Portfolio_2030'], 
               yerr=[df['Portfolio_2030'] - df['Lower_Bound'], 
                     df['Upper_Bound'] - df['Portfolio_2030']], 
               fmt='none', color='black', capsize=8, capthick=2, linewidth=2)
    
    # Formatting
    ax.set_xlabel('Investment Strategy', fontweight='bold')
    ax.set_ylabel('Total Wealth in 2030 (2025 dollars)', fontweight='bold')
    ax.set_title('Comparative Wealth Accumulation (2025-2030) with Variability', 
                fontsize=18, fontweight='bold', color=COLORS['text_dark'], pad=20)
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df['Person'])
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, df['Portfolio_2030'])):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2000, 
               f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Grid
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Close the figure to free memory
    
    return fig

def generate_all_plots(data_dir='data', output_dir='images'):
    """Generate all plots and save them"""
    print("Generating AI Safety Website Plots...")
    print("=" * 50)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate market trends plot
    print("📈 Creating market trends plot...")
    create_market_trends_plot(
        csv_path=f'{data_dir}/market_trends.csv',
        save_path=f'{output_dir}/market_trends.png'
    )
    
    # Generate individual portfolio plots
    for person in ['A', 'B', 'C']:
        print(f"💰 Creating Person {person} portfolio projection...")
        create_portfolio_projection_plot(
            person=person,
            csv_path=f'{data_dir}/person{person}_portfolio.csv',
            save_path=f'{output_dir}/person{person}.png'
        )
    
    # Generate comparative wealth plot
    print("📊 Creating comparative wealth analysis...")
    create_comparative_wealth_plot(
        csv_path=f'{data_dir}/comparative_wealth.csv',
        save_path=f'{output_dir}/comparative_wealth.png'
    )
    
    print("✅ All plots generated successfully!")
    print("🎨 Plots use website color scheme and professional styling")

if __name__ == "__main__":
    generate_all_plots()