# stock-market-dashboard
Real-time stock market dashboard built with Python, Streamlit, and Plotly
# 📈 Real-Time Stock Market Dashboard

A real-time stock market dashboard built with **Python**, **Streamlit**, and **Plotly**.

## Features
- Live stock price charts (candlestick + line)
- Technical indicators: SMA, EMA, RSI, MACD
- Multi-stock comparison
- Auto-refresh with configurable intervals

## Tech Stack
- **Streamlit** — UI framework
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **yfinance / Alpha Vantage** — Market data

## Setup
```bash
git clone https://github.com/YOUR_USERNAME/stock-market-dashboard.git
cd stock-market-dashboard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).