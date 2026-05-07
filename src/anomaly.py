# src/anomaly.py — Isolation Forest anomaly detection on stock OHLCV data

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

BACKGROUND = "#FFFFFF"
GRID       = "#E2E6ED"
TEXT       = "#6B7A99"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    f = pd.DataFrame(index=df.index)
    f["return"]         = df["close"].pct_change()
    f["high_low_range"] = (df["high"] - df["low"]) / df["close"]
    f["open_close"]     = (df["close"] - df["open"]) / df["open"]
    f["volume_change"]  = df["volume"].pct_change()
    f["volume_zscore"]  = (
        (df["volume"] - df["volume"].rolling(20).mean())
        / df["volume"].rolling(20).std()
    )
    f["rolling_std"]    = df["close"].pct_change().rolling(5).std()
    f["gap"]            = (df["open"] - df["close"].shift(1)) / df["close"].shift(1)
    f.replace([np.inf, -np.inf], np.nan, inplace=True)
    f.dropna(inplace=True)
    return f


@st.cache_data(ttl=300)
def detect_anomalies(ticker: str, period: str, contamination: float = 0.05) -> pd.DataFrame:
    from src.data_fetcher import fetch_stock_history
    df = fetch_stock_history(ticker, period)
    if df is None or df.empty or len(df) < 30:
        return pd.DataFrame()
    features = build_features(df)
    if features.empty:
        return pd.DataFrame()
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42, n_jobs=-1)
    model.fit(features)
    scores  = model.decision_function(features)
    labels  = model.predict(features)
    result  = df.loc[features.index].copy()
    result["anomaly_score"] = scores
    result["is_anomaly"]    = labels == -1
    result["severity"]      = result["anomaly_score"].apply(
        lambda s: "High" if s < -0.1 else ("Medium" if s < -0.05 else "Low") if s < 0 else "Normal"
    )
    return result


def get_anomaly_summary(df: pd.DataFrame) -> dict:
    if df.empty or "is_anomaly" not in df.columns:
        return {"total": 0, "anomalies": 0, "pct": 0, "high": 0, "medium": 0, "low": 0, "last_anomaly": "N/A"}
    anomalies = df[df["is_anomaly"]]
    total     = len(df)
    n         = len(anomalies)
    last      = anomalies.index[-1].strftime("%b %d, %Y") if not anomalies.empty else "N/A"
    return {
        "total": total, "anomalies": n, "pct": round(n / total * 100, 1),
        "high":   len(anomalies[anomalies["severity"] == "High"]),
        "medium": len(anomalies[anomalies["severity"] == "Medium"]),
        "low":    len(anomalies[anomalies["severity"] == "Low"]),
        "last_anomaly": last,
    }


def build_anomaly_price_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    if df.empty:
        return go.Figure()
    normal    = df[~df["is_anomaly"]]
    anomalies = df[df["is_anomaly"]]
    high_sev  = anomalies[anomalies["severity"] == "High"]
    med_sev   = anomalies[anomalies["severity"] == "Medium"]
    low_sev   = anomalies[anomalies["severity"] == "Low"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["close"], name="Close", mode="lines",
                             line=dict(color="#38BDF8", width=1.5)))
    for sev_df, color, name, size in [
        (high_sev, "#EF4444", "High anomaly",   12),
        (med_sev,  "#F59E0B", "Medium anomaly",  9),
        (low_sev,  "#6B7280", "Low anomaly",      7),
    ]:
        if not sev_df.empty:
            fig.add_trace(go.Scatter(
                x=sev_df.index, y=sev_df["close"], name=name, mode="markers",
                marker=dict(color=color, size=size, symbol="circle",
                            line=dict(color="white", width=1)),
                hovertemplate=f"<b>{name}</b><br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>",
            ))
    fig.update_layout(
        paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
        font=dict(color=TEXT, size=11), height=400,
        title=dict(text=f"{ticker} — Price with Anomalies", x=0.02, font=dict(size=14, color="#C4CDD8")),
        xaxis=dict(gridcolor=GRID, zeroline=False, rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor=GRID, zeroline=False, side="right", tickprefix="$"),
        legend=dict(bgcolor="rgba(0,0,0,0)", x=0, y=1),
        hovermode="x unified", margin=dict(l=10, r=60, t=40, b=10),
    )
    return fig


def build_anomaly_score_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    if df.empty or "anomaly_score" not in df.columns:
        return go.Figure()
    colors = [
        "#EF4444" if row["is_anomaly"] and row["severity"] == "High"
        else "#F59E0B" if row["is_anomaly"] and row["severity"] == "Medium"
        else "#6B7280" if row["is_anomaly"]
        else "#38BDF8"
        for _, row in df.iterrows()
    ]
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color="rgba(239,68,68,0.4)", width=1.5, dash="dash"),
                  annotation_text="Anomaly threshold", annotation_position="top right",
                  annotation_font=dict(color="#EF4444", size=10))
    fig.add_trace(go.Bar(x=df.index, y=df["anomaly_score"], name="Anomaly score",
                         marker_color=colors,
                         hovertemplate="Date: %{x}<br>Score: %{y:.4f}<extra></extra>"))
    fig.update_layout(
        paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
        font=dict(color=TEXT, size=11), height=240,
        title=dict(text=f"{ticker} — Anomaly Score (below 0 = flagged)", x=0.02,
                   font=dict(size=13, color="#C4CDD8")),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False, side="right"),
        margin=dict(l=10, r=60, t=40, b=10), showlegend=False,
    )
    return fig


def build_feature_importance_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    if df.empty or "is_anomaly" not in df.columns:
        return go.Figure()
    clean = df.drop(columns=["anomaly_score", "is_anomaly", "severity"], errors="ignore")
    features = build_features(clean)
    if features.empty:
        return go.Figure()
    anom_idx   = df[df["is_anomaly"]].index
    normal_idx = df[~df["is_anomaly"]].index
    anom_means   = features.loc[features.index.isin(anom_idx)].mean()
    normal_means = features.loc[features.index.isin(normal_idx)].mean()
    diff = (anom_means - normal_means).abs().sort_values(ascending=True)
    fig  = go.Figure(go.Bar(
        x=diff.values, y=diff.index, orientation="h",
        marker_color="#38BDF8", opacity=0.8,
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
        font=dict(color=TEXT, size=11), height=260,
        title=dict(text="Feature deviation in anomalies vs normal", x=0.02,
                   font=dict(size=13, color="#C4CDD8")),
        xaxis=dict(gridcolor=GRID, zeroline=False, title="Mean absolute deviation"),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        margin=dict(l=10, r=20, t=40, b=10),
    )
    return fig
