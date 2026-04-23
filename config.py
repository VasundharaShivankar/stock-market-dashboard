# config.py — App-wide settings and constants

APP_TITLE = "Stock Market Dashboard"
APP_ICON = "📈"

# Default stocks shown on load
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# Auto-refresh interval options (in seconds)
REFRESH_INTERVALS = {
    "Off": 0,
    "30 seconds": 30,
    "1 minute": 60,
    "5 minutes": 300,
}

# Chart time period options
TIME_PERIODS = {
    "1 Week":   "7d",
    "1 Month":  "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year":   "1y",
    "2 Years":  "2y",
    "5 Years":  "5y",
}

# Chart intervals mapped to periods
INTERVAL_MAP = {
    "7d":  "15m",
    "1mo": "1h",
    "3mo": "1d",
    "6mo": "1d",
    "1y":  "1d",
    "2y":  "1wk",
    "5y":  "1wk",
}

# Technical indicator defaults
INDICATORS = {
    "SMA 20":  {"type": "sma", "window": 20,  "color": "#F59E0B"},
    "SMA 50":  {"type": "sma", "window": 50,  "color": "#3B82F6"},
    "EMA 20":  {"type": "ema", "window": 20,  "color": "#10B981"},
    "EMA 50":  {"type": "ema", "window": 50,  "color": "#8B5CF6"},
}

# Chart colors
COLORS = {
    "up":         "#26A69A",   # green candle
    "down":       "#EF5350",   # red candle
    "volume_up":  "rgba(38,166,154,0.4)",
    "volume_down":"rgba(239,83,80,0.4)",
    "background": "#0E1117",
    "grid":       "#1E2329",
    "text":       "#E0E0E0",
}