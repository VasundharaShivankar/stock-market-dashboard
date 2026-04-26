# 📈 Real-Time Stock Market Dashboard + AI Sentiment Analyzer

A production-grade financial dashboard combining **real-time stock market data** with **AI-powered news sentiment analysis**. Built with Python, Streamlit, and FinBERT — covering two internship projects in one deployed application.

## 🔴 Live Demo
👉 [stock-market-dashboard-6rtnnfin9ctmmke2twg6b7.streamlit.app](https://stock-market-dashboard-6rtnnfin9ctmmke2twg6b7.streamlit.app)

## 📌 Projects Covered
| Project | Description |
|---|---|
| **#4 Real-Time Stock Market Dashboard** | Live stock prices, candlestick charts, technical indicators |
| **#7 AI-Based Sentiment Analyzer** | FinBERT NLP model analyzing stock news sentiment |

---

## ✨ Features

### 📊 Stock Dashboard
- Live stock prices with real-time change and % change
- Candlestick & line charts with full OHLCV data
- Technical indicators — SMA 20/50, EMA 20/50, RSI, MACD, Bollinger Bands
- Volume subplot on price chart
- Multi-stock comparison with normalised % return chart
- Auto-refresh at configurable intervals (30s, 1min, 5min)
- Watchlist — add, switch, and remove tickers on the fly

### 🧠 AI Sentiment Analyzer
- Fetches latest news headlines for any stock via Yahoo Finance
- Runs **FinBERT** (fine-tuned BERT model for financial text) on each headline
- Sentiment scoring — Positive / Neutral / Negative with confidence %
- Overall sentiment score (+100 fully bullish → -100 fully bearish)
- Donut chart — visual breakdown of sentiment distribution
- Horizontal bar chart — per-headline sentiment with confidence
- Color-coded news cards — green (positive), red (negative), grey (neutral)

### ℹ️ Company Info
- Market cap, P/E ratio, 52W high/low
- Sector, industry, dividend yield, average volume
- Company description and website

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | UI framework & deployment |
| Plotly | Interactive financial charts |
| Pandas | Data manipulation |
| yfinance | Real-time Yahoo Finance data |
| ta | Technical analysis indicators |
| FinBERT (Transformers) | NLP sentiment analysis |
| Hugging Face | AI model hosting |
| Python 3.11 | Runtime |

---

## 🚀 Run Locally

```bash
git clone https://github.com/VasundharaShivankar/stock-market-dashboard.git
cd stock-market-dashboard

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
streamlit run app.py
```

> ⚡ First run downloads the FinBERT model (~500MB). Subsequent runs are instant.

---
