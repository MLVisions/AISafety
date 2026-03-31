"""
Market-specific plot generation functions.

Creates interactive Plotly ticker charts, category comparison charts,
and the ticker dropdown JSON used by the economy page.
"""

import json
import os
from datetime import datetime
from typing import Any

import plotly.graph_objects as go  # type: ignore[import-untyped]

from agents.utils.constants import COLORS

from .data_sources import DEFAULT_TICKERS, fetch_maximum_history
from .ticker_constants import (
    CATEGORY_COLORS,
    get_category_description,
    get_ticker_description,
    get_ticker_display_name,
)


# Plotly layout defaults matching the website colour scheme
def _safe_filename(ticker: str) -> str:
    """Convert a ticker symbol to a safe filename component."""
    return ticker.replace("^", "INDEX_").replace("-", "_").replace("=", "_")


_LAYOUT_DEFAULTS: dict[str, Any] = {
    "template": "plotly_white",
    "font": {"family": "Arial, Helvetica, sans-serif", "color": COLORS["text_dark"]},
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "margin": {"l": 60, "r": 30, "t": 60, "b": 50},
    "xaxis": {"gridcolor": "#e8f2fe", "showline": True, "linecolor": COLORS["text_light"]},
    "yaxis": {"gridcolor": "#e8f2fe", "showline": True, "linecolor": COLORS["text_light"]},
    "hovermode": "x unified",
}


def _save_plotly_html(fig: go.Figure, path: str) -> None:
    """Write a self-contained Plotly HTML file (CDN-loaded JS)."""
    fig.write_html(
        path,
        full_html=True,
        include_plotlyjs="cdn",
        config={"responsive": True, "displayModeBar": True, "displaylogo": False},
    )


def create_raw_ticker_plots(output_dir: str = "src/static/images/raw_tickers") -> None:
    """Create interactive Plotly HTML charts for every tracked ticker."""
    os.makedirs(output_dir, exist_ok=True)

    total_created = 0

    for category, tickers in DEFAULT_TICKERS.items():
        color = CATEGORY_COLORS[category]
        for ticker_symbol in tickers:
            try:
                data = fetch_maximum_history(ticker_symbol)
                if data is None or data.empty:
                    continue

                display_name = get_ticker_display_name(ticker_symbol)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data["Date"], y=data["Close"], mode="lines", name="Price",
                    line={"color": color, "width": 2},
                    hovertemplate="%{x|%Y-%m-%d}<br>$%{y:,.2f}<extra></extra>",
                ))

                if len(data) > 50:
                    ma_50 = data["Close"].rolling(window=50).mean()
                    fig.add_trace(go.Scatter(
                        x=data["Date"], y=ma_50, mode="lines", name="50-day MA",
                        line={"color": COLORS["light_gray"], "width": 1, "dash": "dash"},
                        hovertemplate="%{x|%Y-%m-%d}<br>MA50: $%{y:,.2f}<extra></extra>",
                    ))

                if len(data) > 200:
                    ma_200 = data["Close"].rolling(window=200).mean()
                    fig.add_trace(go.Scatter(
                        x=data["Date"], y=ma_200, mode="lines", name="200-day MA",
                        line={"color": COLORS["text_light"], "width": 1, "dash": "dot"},
                        hovertemplate="%{x|%Y-%m-%d}<br>MA200: $%{y:,.2f}<extra></extra>",
                    ))

                start_date = data["Date"].iloc[0].strftime("%Y-%m-%d")
                end_date = data["Date"].iloc[-1].strftime("%Y-%m-%d")

                fig.update_layout(
                    **_LAYOUT_DEFAULTS,
                    title={
                        "text": (
                            f"{display_name}"
                            f"<br><sup>{start_date} to {end_date}  ·  "
                            f"{len(data):,} days  ·  {category.title()}</sup>"
                        ),
                        "x": 0.5, "xanchor": "center",
                    },
                    yaxis_title="Price ($)",
                    legend={"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"},
                    height=500,
                )
                fig.update_xaxes(
                    rangeslider_visible=False,
                    rangeselector={"buttons": [
                        {"count": 6, "label": "6M", "step": "month", "stepmode": "backward"},
                        {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                        {"count": 5, "label": "5Y", "step": "year", "stepmode": "backward"},
                        {"step": "all", "label": "All"},
                    ]},
                )

                safe_filename = _safe_filename(ticker_symbol)
                save_path = os.path.join(output_dir, f"{safe_filename}_historical.html")
                _save_plotly_html(fig, save_path)
                total_created += 1

            except Exception as e:
                print(f"  Warning: No data for {ticker_symbol}: {e}")
                continue

    print(f"  Generated {total_created} interactive ticker charts.")


def create_category_comparison_plots(
    output_dir: str = "src/static/images/category_comparisons",
) -> None:
    """Create interactive normalized comparison charts for each asset category."""
    os.makedirs(output_dir, exist_ok=True)

    total_created = 0

    for category, tickers in DEFAULT_TICKERS.items():
        comparison_tickers = tickers[: min(5, len(tickers))]
        color = CATEGORY_COLORS[category]

        fig = go.Figure()
        successful_plots = 0

        for ticker_sym in comparison_tickers:
            try:
                data = fetch_maximum_history(ticker_sym)
                if data is None or data.empty:
                    continue

                normalized = (data["Close"] / data["Close"].iloc[0]) * 100
                clean_name = ticker_sym.replace("^", "").replace("-USD", "").replace("=F", "")

                fig.add_trace(go.Scatter(
                    x=data["Date"], y=normalized.values, mode="lines",
                    name=clean_name, line={"width": 2},
                    hovertemplate="%{x|%Y-%m-%d}<br>%{y:.1f}<extra>" + clean_name + "</extra>",
                ))
                successful_plots += 1
            except Exception as e:
                print(f"  Error plotting {ticker_sym} in category comparison: {e}")
                continue

        if successful_plots > 0:
            fig.add_hline(y=100, line_dash="dash", line_color=COLORS["text_light"], opacity=0.5)
            fig.update_layout(
                **_LAYOUT_DEFAULTS,
                title={
                    "text": (
                        f"{category.title()} Assets — Normalized Performance"
                        "<br><sup>Starting value = 100</sup>"
                    ),
                    "x": 0.5, "xanchor": "center",
                },
                yaxis_title="Normalized (100 = start)",
                legend={"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"},
                colorway=[color, COLORS["accent_blue"], COLORS["warm_amber"],
                          COLORS["mint_green"], COLORS["coral_pink"]],
                height=500,
            )

            save_path = os.path.join(output_dir, f"{category}_comparison.html")
            _save_plotly_html(fig, save_path)
            total_created += 1

    print(f"  Generated {total_created} interactive category comparison charts.")


def create_ticker_data_files(
    output_dir: str = "src/static/data/tickers",
) -> int:
    """Generate per-ticker JSON data files (weekly) for interactive charting."""
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for category, tickers in DEFAULT_TICKERS.items():
        for ticker_symbol in tickers:
            try:
                data = fetch_maximum_history(ticker_symbol)
                if data is None or data.empty:
                    continue

                # Weekly resample for compact files
                weekly = (
                    data.set_index("Date")["Close"]
                    .resample("W-FRI")
                    .last()
                    .dropna()
                    .reset_index()
                )

                safe_fn = _safe_filename(ticker_symbol)
                ticker_json = {
                    "ticker": ticker_symbol,
                    "name": get_ticker_display_name(ticker_symbol),
                    "category": category,
                    "dates": [d.strftime("%Y-%m-%d") for d in weekly["Date"]],
                    "close": [round(float(v), 2) for v in weekly["Close"]],
                }

                with open(os.path.join(output_dir, f"{safe_fn}.json"), "w") as f:
                    json.dump(ticker_json, f)

                count += 1
            except Exception as e:
                print(f"  Warning: data file for {ticker_symbol}: {e}")

    print(f"  Generated {count} ticker data files.")
    return count


def create_ticker_dropdown_data(
    output_file: str = "src/static/data/ticker_dropdown.json",
) -> dict[str, Any]:
    """Create JSON data structure for the ticker dropdown on the economy page."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    dropdown_data: dict[str, Any] = {
        "categories": {},
        "metadata": {
            "total_tickers": 0,
            "generated_at": datetime.now().isoformat(),
            "description": "Raw ticker historical data for portfolio analysis evidence",
            "defaults": ["^GSPC", "BTC-USD"],
        },
    }

    total_count = 0

    for category, tickers in DEFAULT_TICKERS.items():
        dropdown_data["categories"][category] = {
            "display_name": category.replace("_", " ").title(),
            "description": get_category_description(category),
            "tickers": [],
        }

        for ticker_name in tickers:
            safe_fn = _safe_filename(ticker_name)
            ticker_info = {
                "ticker": ticker_name,
                "display_name": get_ticker_display_name(ticker_name),
                "chart_path": f"images/raw_tickers/{safe_fn}_historical.html",
                "data_path": f"data/tickers/{safe_fn}.json",
                "description": get_ticker_description(ticker_name),
            }
            dropdown_data["categories"][category]["tickers"].append(ticker_info)
            total_count += 1

    dropdown_data["metadata"]["total_tickers"] = total_count

    with open(output_file, "w") as f:
        json.dump(dropdown_data, f, indent=2)

    print(f"  Created ticker dropdown data: {os.path.basename(output_file)}")
    return dropdown_data
