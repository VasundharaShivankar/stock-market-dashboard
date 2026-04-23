# src/data_fetcher.py — Fetches and caches stock data via yfinance

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVAL_MAP


# ─── Cached Data Fetchers ────────────────────────────────────────────────────

@st.cache_data(ttl=60)  # cache for 60 seconds
def fetch_stock_history(ticker: str, period: str) -> pd.DataFrame:
    """
    Fetch OHLCV historical data for a single ticker.
    Returns a clean DataFrame or empty DataFrame on failure.
    """
    try:
        interval = INTERVAL_MAP.get(period, "1d")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            return pd.DataFrame()

        # Clean up the DataFrame
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)  # remove timezone
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.dropna(inplace=True)
        df.columns = ["open", "high", "low", "close", "volume"]

        return df

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_stock_info(ticker: str) -> dict:
    """
    Fetch company metadata: name, sector, market cap, PE ratio, etc.
    Returns a dict with safe fallback values.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "name":        info.get("longName", ticker),
            "sector":      info.get("sector", "N/A"),
            "industry":    info.get("industry", "N/A"),
            "market_cap":  info.get("marketCap", 0),
            "pe_ratio":    info.get("trailingPE", None),
            "52w_high":    info.get("fiftyTwoWeekHigh", None),
            "52w_low":     info.get("fiftyTwoWeekLow", None),
            "avg_volume":  info.get("averageVolume", 0),
            "dividend":    info.get("dividendYield", None),
            "currency":    info.get("currency", "USD"),
            "exchange":    info.get("exchange", "N/A"),
            "website":     info.get("website", ""),
            "description": info.get("longBusinessSummary", ""),
        }

    except Exception:
        return {
            "name": ticker, "sector": "N/A", "industry": "N/A",
            "market_cap": 0, "pe_ratio": None, "52w_high": None,
            "52w_low": None, "avg_volume": 0, "dividend": None,
            "currency": "USD", "exchange": "N/A",
            "website": "", "description": "",
        }


@st.cache_data(ttl=60)
def fetch_live_price(ticker: str) -> dict:
    """
    Fetch the latest price, change, and % change for a ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev    = info.get("previousClose", current)
        change  = current - prev
        pct     = (change / prev * 100) if prev else 0

        return {
            "price":   round(current, 2),
            "change":  round(change, 2),
            "pct":     round(pct, 2),
            "prev":    round(prev, 2),
            "high":    info.get("dayHigh",  current),
            "low":     info.get("dayLow",   current),
            "volume":  info.get("volume",   0),
            "ticker":  ticker,
        }

    except Exception:
        return {
            "price": 0, "change": 0, "pct": 0, "prev": 0,
            "high": 0, "low": 0, "volume": 0, "ticker": ticker,
        }


@st.cache_data(ttl=300)
def fetch_multiple_tickers(tickers: list, period: str) -> dict:
    """
    Fetch historical data for multiple tickers at once.
    Returns a dict of {ticker: DataFrame}.
    """
    results = {}
    for ticker in tickers:
        df = fetch_stock_history(ticker, period)
        if not df.empty:
            results[ticker] = df
    return results


# ─── Helper Utilities ─────────────────────────────────────────────────────────

def validate_ticker(ticker: str) -> bool:
    """Check if a ticker symbol is valid and has data."""
    try:
        stock = yf.Ticker(ticker.upper())
        info  = stock.info
        return bool(info.get("regularMarketPrice") or info.get("currentPrice"))
    except Exception:
        return False


def format_market_cap(value: float) -> str:
    """Format large numbers: 1500000000 → '$1.50B'"""
    if not value:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,.0f}"


def format_volume(value: float) -> str:
    """Format volume: 85000000 → '85.00M'"""
    if not value:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return str(int(value))