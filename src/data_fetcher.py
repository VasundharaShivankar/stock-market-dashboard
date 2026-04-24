# src/data_fetcher.py — Fetches and caches stock data via yfinance

import yfinance as yf
import pandas as pd
import streamlit as st
import requests
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import INTERVAL_MAP

# ─── Shared session with headers to avoid 429 blocks ─────────────────────────

def _make_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session

_SESSION = _make_session()


# ─── Cached Data Fetchers ─────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def fetch_stock_history(ticker: str, period: str) -> pd.DataFrame:
    try:
        interval = INTERVAL_MAP.get(period, "1d")
        stock = yf.Ticker(ticker, session=_SESSION)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.dropna(inplace=True)
        df.columns = ["open", "high", "low", "close", "volume"]
        return df

    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_stock_info(ticker: str) -> dict:
    try:
        time.sleep(0.5)  # small delay to avoid rate limits
        stock = yf.Ticker(ticker, session=_SESSION)
        info  = stock.info

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
    try:
        time.sleep(0.3)
        stock   = yf.Ticker(ticker, session=_SESSION)
        info    = stock.info
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev    = info.get("previousClose", current)
        change  = current - prev
        pct     = (change / prev * 100) if prev else 0

        return {
            "price":  round(current, 2),
            "change": round(change, 2),
            "pct":    round(pct, 2),
            "prev":   round(prev, 2),
            "high":   info.get("dayHigh",  current),
            "low":    info.get("dayLow",   current),
            "volume": info.get("volume",   0),
            "ticker": ticker,
        }

    except Exception:
        return {
            "price": 0, "change": 0, "pct": 0, "prev": 0,
            "high": 0, "low": 0, "volume": 0, "ticker": ticker,
        }


@st.cache_data(ttl=300)
def fetch_multiple_tickers(tickers: list, period: str) -> dict:
    results = {}
    for ticker in tickers:
        df = fetch_stock_history(ticker, period)
        if not df.empty:
            results[ticker] = df
        time.sleep(0.3)  # stagger requests
    return results


# ─── Helper Utilities ─────────────────────────────────────────────────────────

def validate_ticker(ticker: str) -> bool:
    try:
        stock = yf.Ticker(ticker.upper(), session=_SESSION)
        info  = stock.info
        return bool(info.get("regularMarketPrice") or info.get("currentPrice"))
    except Exception:
        return False


def format_market_cap(value: float) -> str:
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
    if not value:
        return "N/A"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return str(int(value))