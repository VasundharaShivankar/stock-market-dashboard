# 📈 Real-Time Stock Market Dashboard

A real-time stock market dashboard built with **Python**, **Streamlit**, and **Plotly**. Tracks live prices, visualises technical indicators, and compares multiple stocks side by side.

## 🔴 Live Demo
👉 [stock-market-dashboard.streamlit.app](https://stock-market-dashboard-7b.streamlit.app)

## ✨ Features

- **Live stock prices** with change and % change
- **Candlestick & line charts** with OHLCV data
- **Technical indicators** — SMA, EMA, RSI, MACD, Bollinger Bands
- **Multi-stock comparison** with normalised % return chart
- **Company info** — market cap, P/E ratio, 52W high/low, sector
- **Auto-refresh** at configurable intervals
- **Watchlist** — add, switch, and remove tickers on the fly

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | UI framework |
| Plotly | Interactive charts |
| Pandas | Data manipulation |
| yfinance | Yahoo Finance data |
| ta | Technical indicators |
| Python 3.11 | Runtime |

## 🚀 Run Locally

```bash
git clone https://github.com/VasundharaShivankar/stock-market-dashboard.git
cd stock-market-dashboard
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure