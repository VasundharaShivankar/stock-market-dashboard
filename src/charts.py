# src/charts.py — Plotly chart builders for the stock dashboard

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS
from src.indicators import add_all_indicators


# ─── Layout Defaults ──────────────────────────────────────────────────────────

LAYOUT = dict(
    paper_bgcolor = COLORS["background"],
    plot_bgcolor  = COLORS["background"],
    font          = dict(color=COLORS["text"], size=12),
    xaxis         = dict(
        gridcolor     = COLORS["grid"],
        showgrid      = True,
        zeroline      = False,
        rangeslider   = dict(visible=False),
    ),
    yaxis         = dict(
        gridcolor = COLORS["grid"],
        showgrid  = True,
        zeroline  = False,
        side      = "right",
    ),
    margin        = dict(l=10, r=60, t=40, b=10),
    legend        = dict(
        bgcolor     = "rgba(0,0,0,0)",
        bordercolor = COLORS["grid"],
        borderwidth = 1,
        x=0, y=1,
    ),
    hovermode = "x unified",
)


# ─── Main Price Chart ─────────────────────────────────────────────────────────

def build_price_chart(
    df: pd.DataFrame,
    ticker: str,
    chart_type: str = "Candlestick",
    indicators: list = [],
    show_volume: bool = True,
    show_bollinger: bool = False,
) -> go.Figure:
    """
    Main price chart with optional overlays and volume subplot.
    chart_type: 'Candlestick' or 'Line'
    indicators: list of strings e.g. ['SMA 20', 'EMA 50']
    """
    if df.empty:
        return _empty_figure(f"No data available for {ticker}")

    enriched = add_all_indicators(df)

    # ── Subplot layout ───────────────────────────────────────────────────────
    row_heights = [0.6, 0.2] if show_volume else [1.0]
    rows        = 2 if show_volume else 1

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # ── Price trace ──────────────────────────────────────────────────────────
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x     = enriched.index,
            open  = enriched["open"],
            high  = enriched["high"],
            low   = enriched["low"],
            close = enriched["close"],
            name  = ticker,
            increasing_line_color = COLORS["up"],
            decreasing_line_color = COLORS["down"],
            increasing_fillcolor  = COLORS["up"],
            decreasing_fillcolor  = COLORS["down"],
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x    = enriched.index,
            y    = enriched["close"],
            name = ticker,
            mode = "lines",
            line = dict(color=COLORS["up"], width=2),
            fill = "tozeroy",
            fillcolor = "rgba(38,166,154,0.08)",
        ), row=1, col=1)

    # ── Bollinger Bands ──────────────────────────────────────────────────────
    if show_bollinger and "bb_upper" in enriched.columns:
        fig.add_trace(go.Scatter(
            x=enriched.index, y=enriched["bb_upper"],
            name="BB Upper", mode="lines",
            line=dict(color="rgba(150,150,255,0.5)", width=1, dash="dot"),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=enriched.index, y=enriched["bb_lower"],
            name="BB Lower", mode="lines",
            line=dict(color="rgba(150,150,255,0.5)", width=1, dash="dot"),
            fill="tonexty",
            fillcolor="rgba(150,150,255,0.05)",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=enriched.index, y=enriched["bb_mid"],
            name="BB Mid", mode="lines",
            line=dict(color="rgba(150,150,255,0.3)", width=1),
        ), row=1, col=1)

    # ── Moving Average overlays ───────────────────────────────────────────────
    indicator_map = {
        "SMA 20": ("sma_20", "#F59E0B"),
        "SMA 50": ("sma_50", "#3B82F6"),
        "EMA 20": ("ema_20", "#10B981"),
        "EMA 50": ("ema_50", "#8B5CF6"),
    }
    for label, (col, color) in indicator_map.items():
        if label in indicators and col in enriched.columns:
            fig.add_trace(go.Scatter(
                x=enriched.index, y=enriched[col],
                name=label, mode="lines",
                line=dict(color=color, width=1.5),
            ), row=1, col=1)

    # ── Volume bars ───────────────────────────────────────────────────────────
    if show_volume:
        colors = [
            COLORS["volume_up"] if c >= o else COLORS["volume_down"]
            for c, o in zip(enriched["close"], enriched["open"])
        ]
        fig.add_trace(go.Bar(
            x=enriched.index, y=enriched["volume"],
            name="Volume", marker_color=colors,
            showlegend=False,
        ), row=2, col=1)

    # ── Layout ────────────────────────────────────────────────────────────────
    layout = LAYOUT.copy()
    layout["title"] = dict(text=f"{ticker} — Price Chart", x=0.02, font=dict(size=16))
    layout["xaxis2"] = dict(gridcolor=COLORS["grid"], showgrid=True, zeroline=False)
    layout["yaxis2"] = dict(gridcolor=COLORS["grid"], showgrid=True,
                             zeroline=False, side="right", title="Volume")
    layout["height"]  = 560 if show_volume else 460

    fig.update_layout(**layout)
    return fig


# ─── RSI Chart ────────────────────────────────────────────────────────────────

def build_rsi_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """RSI oscillator with overbought/oversold bands."""
    if df.empty or len(df) < 15:
        return _empty_figure("Not enough data for RSI")

    enriched = add_all_indicators(df)

    fig = go.Figure()

    fig.add_hline(y=70, line=dict(color="rgba(239,83,80,0.5)",  width=1, dash="dash"))
    fig.add_hline(y=30, line=dict(color="rgba(38,166,154,0.5)", width=1, dash="dash"))
    fig.add_hline(y=50, line=dict(color="rgba(200,200,200,0.2)", width=1))

    fig.add_trace(go.Scatter(
        x=enriched.index, y=enriched["rsi"],
        name="RSI (14)", mode="lines",
        line=dict(color="#F59E0B", width=2),
        fill="tozeroy",
        fillcolor="rgba(245,158,11,0.06)",
    ))

    layout = LAYOUT.copy()
    layout["title"]  = dict(text=f"{ticker} — RSI (14)", x=0.02, font=dict(size=14))
    layout["height"] = 260
    layout["yaxis"]  = dict(
        range=[0, 100], gridcolor=COLORS["grid"],
        tickvals=[30, 50, 70], side="right",
        ticktext=["30 Oversold", "50", "70 Overbought"],
    )
    fig.update_layout(**layout)
    return fig


# ─── MACD Chart ───────────────────────────────────────────────────────────────

def build_macd_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """MACD line, signal line, and histogram."""
    if df.empty or len(df) < 27:
        return _empty_figure("Not enough data for MACD")

    enriched = add_all_indicators(df)

    fig = go.Figure()

    # Histogram bars (green positive, red negative)
    hist_colors = [
        COLORS["up"] if v >= 0 else COLORS["down"]
        for v in enriched["macd_histogram"]
    ]
    fig.add_trace(go.Bar(
        x=enriched.index, y=enriched["macd_histogram"],
        name="Histogram", marker_color=hist_colors,
        opacity=0.6,
    ))

    fig.add_trace(go.Scatter(
        x=enriched.index, y=enriched["macd"],
        name="MACD", mode="lines",
        line=dict(color="#3B82F6", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=enriched.index, y=enriched["macd_signal"],
        name="Signal", mode="lines",
        line=dict(color="#F59E0B", width=1.5),
    ))

    layout = LAYOUT.copy()
    layout["title"]  = dict(text=f"{ticker} — MACD", x=0.02, font=dict(size=14))
    layout["height"] = 280
    fig.update_layout(**layout)
    return fig


# ─── Multi-Stock Comparison Chart ─────────────────────────────────────────────

def build_comparison_chart(data: dict) -> go.Figure:
    """
    Normalised % return comparison for multiple tickers.
    data: {ticker: DataFrame}
    """
    if not data:
        return _empty_figure("No data to compare")

    PALETTE = ["#26A69A", "#3B82F6", "#F59E0B", "#8B5CF6", "#EF5350"]
    fig = go.Figure()

    for i, (ticker, df) in enumerate(data.items()):
        if df.empty:
            continue
        base  = df["close"].iloc[0]
        pct   = ((df["close"] - base) / base) * 100
        color = PALETTE[i % len(PALETTE)]

        fig.add_trace(go.Scatter(
            x=df.index, y=pct,
            name=ticker, mode="lines",
            line=dict(color=color, width=2),
        ))

    fig.add_hline(y=0, line=dict(color="rgba(200,200,200,0.3)", width=1))

    layout = LAYOUT.copy()
    layout["title"]  = dict(text="Return Comparison (%)", x=0.02, font=dict(size=16))
    layout["height"] = 420
    layout["yaxis"]  = dict(
        gridcolor=COLORS["grid"], showgrid=True,
        zeroline=False, side="right", ticksuffix="%",
    )
    fig.update_layout(**layout)
    return fig


# ─── Utility ──────────────────────────────────────────────────────────────────

def _empty_figure(message: str) -> go.Figure:
    """Returns a blank dark chart with a centred message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=COLORS["text"], size=14),
    )
    fig.update_layout(
        paper_bgcolor=COLORS["background"],
        plot_bgcolor =COLORS["background"],
        height=300,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig