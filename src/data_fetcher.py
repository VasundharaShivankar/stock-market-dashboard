# src/data_fetcher.py — yfinance 1.3.0 compatible

import yfinance as yf
import pandas as pd
import streamlit as st
import functools
import logging
import time
from config import INTERVAL_MAP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Retry Decorator ──────────────────────────────────────────────────────────

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"{func.__name__} attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)
            logger.error(f"{func.__name__} failed after {max_attempts} attempts")
            return None
        return wrapper
    return decorator


# ─── Cached Data Fetchers ─────────────────────────────────────────────────────

@st.cache_data(ttl=60)
@retry(max_attempts=3, delay=1.0)
def fetch_stock_history(ticker: str, period: str) -> pd.DataFrame:
    interval = INTERVAL_MAP.get(period, "1d")
    t  = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval, auto_adjust=True)

    if df is None or df.empty:
        return pd.DataFrame()

    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]
    keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df   = df[keep]
    df.dropna(inplace=True)
    return df


@st.cache_data(ttl=300)
def fetch_stock_info(ticker: str) -> dict:
    try:
        time.sleep(0.5)
        t    = yf.Ticker(ticker)
        info = t.info
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
@retry(max_attempts=3, delay=1.0)
def fetch_live_price(ticker: str) -> dict:
    t       = yf.Ticker(ticker)
    fi      = t.fast_info
    current = getattr(fi, "last_price",     None) or 0
    prev    = getattr(fi, "previous_close", current)
    high    = getattr(fi, "day_high",       current)
    low     = getattr(fi, "day_low",        current)
    volume  = getattr(fi, "last_volume",    0)
    change  = current - prev
    pct     = (change / prev * 100) if prev else 0
    return {
        "price":  round(float(current), 2),
        "change": round(float(change),  2),
        "pct":    round(float(pct),     2),
        "prev":   round(float(prev),    2),
        "high":   round(float(high),    2),
        "low":    round(float(low),     2),
        "volume": int(volume),
        "ticker": ticker,
    }


@st.cache_data(ttl=300)
def fetch_multiple_tickers(tickers: list, period: str) -> dict:
    results = {}
    for ticker in tickers:
        df = fetch_stock_history(ticker, period)
        if df is not None and not df.empty:
            results[ticker] = df
        time.sleep(0.3)
    return results


# ─── Helpers ──────────────────────────────────────────────────────────────────

def validate_ticker(ticker: str) -> bool:
    try:
        fi = yf.Ticker(ticker.upper()).fast_info
        return bool(getattr(fi, "last_price", None))
    except Exception:
        return False


def format_market_cap(value: float) -> str:
    if not value:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value/1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    return f"${value:,.0f}"


def format_volume(value: float) -> str:
    if not value:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value/1_000:.2f}K"
    return str(int(value))