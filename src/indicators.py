# src/indicators.py — Technical indicator calculations using Pandas + ta library

import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def add_sma(df: pd.DataFrame, window: int) -> pd.Series:
    """Simple Moving Average"""
    return SMAIndicator(close=df["close"], window=window).sma_indicator()


def add_ema(df: pd.DataFrame, window: int) -> pd.Series:
    """Exponential Moving Average"""
    return EMAIndicator(close=df["close"], window=window).ema_indicator()


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Relative Strength Index (0–100). Overbought >70, Oversold <30"""
    return RSIIndicator(close=df["close"], window=window).rsi()


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    MACD line, Signal line, and Histogram.
    Returns a DataFrame with columns: macd, signal, histogram
    """
    macd = MACD(close=df["close"])
    return pd.DataFrame({
        "macd":      macd.macd(),
        "signal":    macd.macd_signal(),
        "histogram": macd.macd_diff(),
    }, index=df.index)


def add_bollinger_bands(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Bollinger Bands: upper, middle (SMA), lower bands.
    Returns DataFrame with columns: bb_upper, bb_mid, bb_lower
    """
    bb = BollingerBands(close=df["close"], window=window)
    return pd.DataFrame({
        "bb_upper": bb.bollinger_hband(),
        "bb_mid":   bb.bollinger_mavg(),
        "bb_lower": bb.bollinger_lband(),
    }, index=df.index)


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds all indicators to a copy of the DataFrame.
    Returns enriched DataFrame.
    """
    if df.empty or len(df) < 26:
        return df

    out = df.copy()

    # Moving averages
    out["sma_20"] = add_sma(df, 20)
    out["sma_50"] = add_sma(df, 50)
    out["ema_20"] = add_ema(df, 20)
    out["ema_50"] = add_ema(df, 50)

    # RSI
    out["rsi"] = add_rsi(df)

    # MACD
    macd_df = add_macd(df)
    out["macd"]           = macd_df["macd"]
    out["macd_signal"]    = macd_df["signal"]
    out["macd_histogram"] = macd_df["histogram"]

    # Bollinger Bands
    bb_df = add_bollinger_bands(df)
    out["bb_upper"] = bb_df["bb_upper"]
    out["bb_mid"]   = bb_df["bb_mid"]
    out["bb_lower"] = bb_df["bb_lower"]

    return out