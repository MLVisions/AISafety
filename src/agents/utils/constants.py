"""
Centralized visual constants for the AI Safety website.

Single source of truth for colors, palette, and plot styling
used across builders and market modules.  Market-specific ticker
constants live in ``src.market.ticker_constants``.
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
