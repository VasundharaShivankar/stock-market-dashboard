# app.py — Stock Market Dashboard
 
import streamlit as st
import pandas as pd
import time
from config import (
    APP_TITLE, APP_ICON,
    REFRESH_INTERVALS, TIME_PERIODS,
)
from src.data_fetcher import (
    fetch_stock_history, fetch_stock_info,
    fetch_live_price, fetch_multiple_tickers,
    validate_ticker, format_market_cap, format_volume,
)
from src.charts import (
    build_price_chart, build_rsi_chart,
    build_macd_chart, build_comparison_chart,
)
from src.errors import (
    show_empty_state, show_error_card,
    show_warning_card, show_success_card,
    validate_and_show_error,
)
 
# ─── Page Config ──────────────────────────────────────────────────────────────
 
st.set_page_config(
    page_title            = APP_TITLE,
    page_icon             = APP_ICON,
    layout                = "wide",
    initial_sidebar_state = "expanded",
)
 
# ─── CSS ──────────────────────────────────────────────────────────────────────
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
 
html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #F0F2F5 !important;
    color: #111827 !important;
}
 
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: #1B3A6B;
    z-index: 9999;
}
 
.main .block-container {
    padding: 2rem 2rem 3rem !important;
    max-width: 1400px !important;
    background: #F0F2F5 !important;
}
 
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"]        { display: none !important; }
 
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #DDE1E9 !important;
    min-width: 265px !important;
    max-width: 265px !important;
    transform: none !important;
    visibility: visible !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
 
[data-testid="stSidebar"] .stMarkdown h4 {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #9CA3AF !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #9CA3AF !important;
}
[data-testid="stSidebar"] input {
    background: #F9FAFB !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    color: #111827 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: #1B3A6B !important;
    box-shadow: 0 0 0 3px rgba(27,58,107,0.1) !important;
    background: #FFFFFF !important;
}
[data-testid="stSidebar"] input::placeholder { color: #9CA3AF !important; }
 
[data-testid="stSidebar"] .stButton button {
    background: #F9FAFB !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    color: #374151 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    text-align: left !important;
    padding: 0.4rem 0.75rem !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #EEF2FF !important;
    border-color: #1B3A6B !important;
    color: #1B3A6B !important;
}
 
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #F9FAFB !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    color: #111827 !important;
    font-size: 0.85rem !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    color: #374151 !important;
    font-family: 'Inter', sans-serif !important;
}
 
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-top: 3px solid #1B3A6B !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.07) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    text-transform: uppercase !important;
    color: #6B7280 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.25rem !important;
    font-weight: 500 !important;
    color: #111827 !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
 
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid #E5E7EB !important;
    padding: 0 !important;
    border-radius: 0 !important;
    width: 100% !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #6B7280 !important;
    padding: 10px 18px !important;
    margin-bottom: -2px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: color 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1B3A6B !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #1B3A6B !important;
    border-bottom: 2px solid #1B3A6B !important;
    font-weight: 600 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
 
.price-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: #111827;
    line-height: 1;
    letter-spacing: -0.02em;
}
.price-change-pos {
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    color: #166534;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 4px;
    padding: 2px 8px;
    margin-top: 5px;
}
.price-change-neg {
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    color: #991B1B;
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 4px;
    padding: 2px 8px;
    margin-top: 5px;
}
 
.ticker-badge {
    display: inline-flex;
    align-items: center;
    background: #1B3A6B;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
    text-transform: uppercase;
}
 
.company-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    color: #374151;
    margin: 0;
    line-height: 1.4;
}
 
.section-divider {
    border: none;
    border-top: 1px solid #E5E7EB;
    margin: 1.25rem 0;
}
 
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}
 
.stAlert {
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
 
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F0F2F5; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }
 
.app-logo {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 1px;
    letter-spacing: -0.01em;
}
.app-tagline {
    font-size: 0.6rem;
    color: #9CA3AF;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 0;
}
 
.status-live {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #166534;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 2px 8px;
}
.status-live::before {
    content: '';
    width: 5px;
    height: 5px;
    background: #16A34A;
    border-radius: 50%;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%,100%{ opacity:1; }
    50%    { opacity:0.2; }
}
 
.sidebar-header {
    padding: 1.25rem 1.25rem 1rem;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 0.75rem;
}
.sidebar-section {
    padding: 0 1.25rem;
}
.sidebar-section-label {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9CA3AF;
    font-family: 'Inter', sans-serif;
    padding-bottom: 0.4rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #F3F4F6;
    display: block;
    margin-top: 1rem;
}
 
.stCaption, [data-testid="stCaptionContainer"] p {
    font-family: 'Inter', sans-serif !important;
    color: #9CA3AF !important;
    font-size: 0.7rem !important;
}
 
.stSpinner > div { border-top-color: #1B3A6B !important; }
 
@media (max-width: 900px) {
    .main .block-container { padding: 1rem 1rem 2rem !important; }
    .price-header { font-size: 1.5rem !important; }
}
@media (max-width: 600px) {
    .price-header { font-size: 1.2rem !important; }
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
}
 
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style='
    background: #1B3A6B;
    padding: 0.75rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -2rem -2rem 1.5rem -2rem;
    border-bottom: 1px solid #162f5a;
'>
    <div style='display:flex;align-items:center;gap:16px'>
        <div style='
            background: #FFFFFF;
            border-radius: 6px;
            width: 32px; height: 32px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem;
        '>📈</div>
        <div>
            <div style='
                font-family: JetBrains Mono, monospace;
                font-size: 0.85rem;
                font-weight: 600;
                color: #FFFFFF;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            '>Stock Market Dashboard</div>
            <div style='
                font-size: 0.65rem;
                color: rgba(255,255,255,0.5);
                letter-spacing: 0.1em;
                text-transform: uppercase;
                font-weight: 500;
            '>Market Intelligence Platform</div>
        </div>
    </div>
    <div style='display:flex;align-items:center;gap:20px'>
        <div style='
            font-size:0.7rem;color:rgba(255,255,255,0.5);
            font-family:Inter,sans-serif;letter-spacing:.04em
        '>Data via Yahoo Finance</div>
        <div style='
            display:inline-flex;align-items:center;gap:5px;
            font-size:0.65rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#4ADE80;
            background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.25);
            border-radius:20px;padding:3px 10px;
        '>
            <span style='width:5px;height:5px;background:#4ADE80;border-radius:50%;
            display:inline-block;animation:hdr-blink 2s infinite'></span>
            Live
        </div>
    </div>
</div>
<style>
@keyframes hdr-blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
</style>
""", unsafe_allow_html=True)
 
# ─── Session State ─────────────────────────────────────────────────────────────
 
if "tickers"       not in st.session_state:
    st.session_state.tickers       = ["AAPL", "MSFT"]
if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = "AAPL"
if "last_refresh"  not in st.session_state:
    st.session_state.last_refresh  = time.time()
 
# Empty watchlist guard
if not st.session_state.tickers:
    show_empty_state(
        "Your watchlist is empty. Add a ticker from the sidebar to get started.",
        icon="📈"
    )
 
 
# ─── Sidebar ──────────────────────────────────────────────────────────────────
 
with st.sidebar:
 
    # Header
    st.markdown("""
        <div class='sidebar-header'>
            <div class='app-logo'>📈 Stock Dashboard</div>
            <div class='app-tagline'>Market Intelligence Platform</div>
            <div style='margin-top:8px'><span class='status-live'>Live Data</span></div>
        </div>
    """, unsafe_allow_html=True)
 
    # ── Add Stock ─────────────────────────────────────────────────────────────
    st.markdown("<span class='sidebar-section-label'>Add Stock</span>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            new_ticker = st.text_input(
                "Ticker", placeholder="e.g. TSLA",
                label_visibility="collapsed"
            ).upper().strip()
        with col2:
            add_clicked = st.button("Add", use_container_width=True)
 
    if add_clicked and new_ticker:
        if new_ticker in st.session_state.tickers:
            show_warning_card(f"{new_ticker} is already in your watchlist.")
        else:
            with st.spinner(f"Validating {new_ticker}..."):
                if validate_ticker(new_ticker):
                    st.session_state.tickers.append(new_ticker)
                    st.session_state.active_ticker = new_ticker
                    show_success_card(f"{new_ticker} added!")
                    st.rerun()
                else:
                    show_error_card(f"'{new_ticker}' not found.", "Check the symbol and try again.")
 
    # ── Watchlist ─────────────────────────────────────────────────────────────
    st.markdown("<span class='sidebar-section-label'>Watchlist</span>", unsafe_allow_html=True)
    for t in list(st.session_state.tickers):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            active = t == st.session_state.active_ticker
            label  = f"▶  {t}" if active else f"    {t}"
            if st.button(label, key=f"btn_{t}", use_container_width=True):
                st.session_state.active_ticker = t
                st.rerun()
        with col_b:
            if st.button("✕", key=f"del_{t}", help=f"Remove {t}"):
                st.session_state.tickers.remove(t)
                if st.session_state.active_ticker == t:
                    st.session_state.active_ticker = (
                        st.session_state.tickers[0]
                        if st.session_state.tickers else ""
                    )
                st.rerun()
 
    # ── Chart Settings ────────────────────────────────────────────────────────
    st.markdown("<span class='sidebar-section-label'>Chart Settings</span>", unsafe_allow_html=True)
 
    period = st.selectbox(
        "Time Period",
        options=list(TIME_PERIODS.keys()),
        index=2,
        label_visibility="collapsed",
    )
    period_code = TIME_PERIODS[period]
 
    st.caption("Time Period")
    chart_type = st.radio(
        "Chart Type",
        options=["Candlestick", "Line"],
        horizontal=True,
        label_visibility="collapsed",
    )
 
    st.markdown("<span class='sidebar-section-label'>Overlays</span>", unsafe_allow_html=True)
    show_sma20  = st.checkbox("SMA 20",          value=True)
    show_sma50  = st.checkbox("SMA 50",          value=True)
    show_ema20  = st.checkbox("EMA 20",          value=False)
    show_ema50  = st.checkbox("EMA 50",          value=False)
    show_bb     = st.checkbox("Bollinger Bands", value=False)
    show_volume = st.checkbox("Volume",          value=True)
 
    st.markdown("<span class='sidebar-section-label'>Oscillators</span>", unsafe_allow_html=True)
    show_rsi  = st.checkbox("RSI",  value=True)
    show_macd = st.checkbox("MACD", value=True)
 
    # ── Auto Refresh ──────────────────────────────────────────────────────────
    st.markdown("<span class='sidebar-section-label'>Auto Refresh</span>", unsafe_allow_html=True)
    refresh_label = st.selectbox(
        "Interval",
        options=list(REFRESH_INTERVALS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    refresh_secs = REFRESH_INTERVALS[refresh_label]
 
    if refresh_secs > 0:
        elapsed   = time.time() - st.session_state.last_refresh
        remaining = max(0, refresh_secs - elapsed)
        st.caption(f"Next refresh in {int(remaining)}s")
        if elapsed >= refresh_secs:
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Data · Yahoo Finance  |  yfinance 1.3.0")
 
 
# ─── Guard ────────────────────────────────────────────────────────────────────
 
ticker = st.session_state.active_ticker
if not ticker:
    st.stop()
 
 
# ─── Tabs ─────────────────────────────────────────────────────────────────────
 
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Chart",
    "🔁  Compare",
    "ℹ️  Info",
    "🧠  Sentiment",
    "🚨  Anomaly",
])
 
 
# ════════════════════════════════════════════════════════════════════
# TAB 1 — CHART
# ════════════════════════════════════════════════════════════════════
with tab1:
 
    price_data = fetch_live_price(ticker)
    info_data  = fetch_stock_info(ticker)
 
    # ── Header row ────────────────────────────────────────────────────────────
    col_name, col_price, col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 1, 1, 1, 1])
 
    with col_name:
        st.markdown(
            f"<div class='ticker-badge'>{ticker}</div>"
            f"<div class='company-name'>{info_data['name']}</div>",
            unsafe_allow_html=True
        )
 
    with col_price:
        sign = "+" if price_data["change"] >= 0 else ""
        cls  = "price-change-pos" if price_data["change"] >= 0 else "price-change-neg"
        arrow = "▲" if price_data["change"] >= 0 else "▼"
        st.markdown(
            f"<div class='price-header'>${price_data['price']:,.2f}</div>"
            f"<div class='{cls}'>{arrow} {sign}{price_data['change']:.2f} "
            f"({sign}{price_data['pct']:.2f}%)</div>",
            unsafe_allow_html=True
        )
 
    with col_m1:
        st.metric("Day High",   f"${price_data['high']:,.2f}")
    with col_m2:
        st.metric("Day Low",    f"${price_data['low']:,.2f}")
    with col_m3:
        st.metric("Prev Close", f"${price_data['prev']:,.2f}")
    with col_m4:
        st.metric("Volume",     format_volume(price_data["volume"]))
 
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
    # ── Indicators ────────────────────────────────────────────────────────────
    selected_indicators = []
    if show_sma20: selected_indicators.append("SMA 20")
    if show_sma50: selected_indicators.append("SMA 50")
    if show_ema20: selected_indicators.append("EMA 20")
    if show_ema50: selected_indicators.append("EMA 50")
 
    # ── Fetch & validate ──────────────────────────────────────────────────────
    with st.spinner(f"Loading {ticker}  ·  {period}..."):
        df = fetch_stock_history(ticker, period_code)
 
    if df is None:
        df = pd.DataFrame()
 
    if not validate_and_show_error(ticker, df):
        st.stop()
 
    # ── Charts ────────────────────────────────────────────────────────────────
    st.plotly_chart(
        build_price_chart(
            df, ticker, chart_type,
            indicators     = selected_indicators,
            show_volume    = show_volume,
            show_bollinger = show_bb,
        ),
        use_container_width=True
    )
 
    if show_rsi:
        if len(df) >= 15:
            st.plotly_chart(build_rsi_chart(df, ticker), use_container_width=True)
        else:
            show_warning_card(f"Not enough data for RSI ({len(df)} bars). Try a longer period.")
 
    if show_macd:
        if len(df) >= 27:
            st.plotly_chart(build_macd_chart(df, ticker), use_container_width=True)
        else:
            show_warning_card(f"Not enough data for MACD ({len(df)} bars). Try a longer period.")
 
    st.caption(f"Last updated  ·  {time.strftime('%H:%M:%S')}  ·  {period} period  ·  {len(df)} bars")
 
 
# ════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Return Comparison")
    st.caption("Normalised % return from the start of the selected period.")
 
    compare_tickers = st.multiselect(
        "Select stocks to compare",
        options = st.session_state.tickers,
        default = st.session_state.tickers[:min(3, len(st.session_state.tickers))],
    )
 
    if len(compare_tickers) < 2:
        show_empty_state("Select at least 2 stocks to compare.", icon="🔁")
    else:
        with st.spinner("Loading comparison data..."):
            compare_data = fetch_multiple_tickers(compare_tickers, period_code)
 
        if not compare_data:
            show_error_card(
                "Could not load comparison data.",
                "Try selecting different stocks or a different time period."
            )
        else:
            st.plotly_chart(
                build_comparison_chart(compare_data),
                use_container_width=True
            )
 
            st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            st.markdown("#### Period Summary")
            rows = []
            for sym, d in compare_data.items():
                if d is None or d.empty:
                    continue
                start = d["close"].iloc[0]
                end   = d["close"].iloc[-1]
                ret   = ((end - start) / start) * 100
                rows.append({
                    "Ticker":      sym,
                    "Start":       f"${start:.2f}",
                    "End":         f"${end:.2f}",
                    "Return":      f"{ret:+.2f}%",
                    "Period High": f"${d['high'].max():.2f}",
                    "Period Low":  f"${d['low'].min():.2f}",
                })
            if rows:
                st.dataframe(
                    pd.DataFrame(rows).set_index("Ticker"),
                    use_container_width=True,
                )
 
 
# ════════════════════════════════════════════════════════════════════
# TAB 3 — INFO
# ════════════════════════════════════════════════════════════════════
with tab3:
    info_data = fetch_stock_info(ticker)
 
    st.markdown(f"### {info_data['name']}")
    st.markdown(
        f"`{ticker}` &nbsp;·&nbsp; {info_data['exchange']} &nbsp;·&nbsp; {info_data['currency']}",
        unsafe_allow_html=True
    )
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1:
        st.metric("Market Cap", format_market_cap(info_data["market_cap"]))
    with col_i2:
        pe = info_data["pe_ratio"]
        st.metric("P/E Ratio",  f"{pe:.2f}" if pe else "N/A")
    with col_i3:
        hi = info_data["52w_high"]
        st.metric("52W High",   f"${hi:.2f}" if hi else "N/A")
    with col_i4:
        lo = info_data["52w_low"]
        st.metric("52W Low",    f"${lo:.2f}" if lo else "N/A")
 
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
    col_i5, col_i6 = st.columns(2)
    with col_i5:
        div_str = "N/A" if not info_data["dividend"] else f"{info_data['dividend']*100:.2f}%"
        st.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem'>"
            f"<p style='font-size:0.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:#9CA3AF;margin:0 0 12px'>Company Details</p>"
            f"<table style='width:100%;font-size:0.85rem;border-collapse:collapse'>"
            f"<tr><td style='color:#6B7280;padding:6px 0;border-bottom:1px solid #F3F4F6'>Sector</td>"
            f"<td style='text-align:right;font-weight:500;padding:6px 0;border-bottom:1px solid #F3F4F6'>{info_data['sector']}</td></tr>"
            f"<tr><td style='color:#6B7280;padding:6px 0;border-bottom:1px solid #F3F4F6'>Industry</td>"
            f"<td style='text-align:right;font-weight:500;padding:6px 0;border-bottom:1px solid #F3F4F6'>{info_data['industry']}</td></tr>"
            f"<tr><td style='color:#6B7280;padding:6px 0;border-bottom:1px solid #F3F4F6'>Avg Volume</td>"
            f"<td style='text-align:right;font-weight:500;font-family:JetBrains Mono,monospace;padding:6px 0;border-bottom:1px solid #F3F4F6'>{format_volume(info_data['avg_volume'])}</td></tr>"
            f"<tr><td style='color:#6B7280;padding:6px 0'>Dividend Yield</td>"
            f"<td style='text-align:right;font-weight:500;padding:6px 0'>{div_str}</td></tr>"
            f"</table></div>",
            unsafe_allow_html=True
        )
    with col_i6:
        website_html = (
            f"<a href='{info_data['website']}' target='_blank' "
            f"style='color:#1B3A6B;font-size:0.82rem'>{info_data['website']}</a>"
            if info_data["website"] else "<span style='color:#9CA3AF'>N/A</span>"
        )
        st.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem'>"
            f"<p style='font-size:0.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:#9CA3AF;margin:0 0 12px'>Exchange Info</p>"
            f"<table style='width:100%;font-size:0.85rem;border-collapse:collapse'>"
            f"<tr><td style='color:#6B7280;padding:6px 0;border-bottom:1px solid #F3F4F6'>Exchange</td>"
            f"<td style='text-align:right;font-weight:500;padding:6px 0;border-bottom:1px solid #F3F4F6'>{info_data['exchange']}</td></tr>"
            f"<tr><td style='color:#6B7280;padding:6px 0;border-bottom:1px solid #F3F4F6'>Currency</td>"
            f"<td style='text-align:right;font-weight:500;padding:6px 0;border-bottom:1px solid #F3F4F6'>{info_data['currency']}</td></tr>"
            f"<tr><td style='color:#6B7280;padding:6px 0'>Website</td>"
            f"<td style='text-align:right;padding:6px 0'>{website_html}</td></tr>"
            f"</table></div>",
            unsafe_allow_html=True
        )
 
    if info_data["description"]:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:#FFFFFF;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem'>"
            f"<p style='font-size:0.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;"
            f"color:#9CA3AF;margin:0 0 10px'>About</p>"
            f"<p style='font-size:0.875rem;color:#374151;line-height:1.7;margin:0'>"
            f"{info_data['description'][:600]}...</p>"
            f"</div>",
            unsafe_allow_html=True
        )
 
 
# ════════════════════════════════════════════════════════════════════
# TAB 4 — SENTIMENT
# ════════════════════════════════════════════════════════════════════
with tab4:
    from src.sentiment import (
        analyze_sentiment, get_overall_sentiment,
        build_sentiment_bar_chart, build_sentiment_donut,
        load_sentiment_model,
    )
 
    st.markdown("### AI News Sentiment")
    st.caption(f"FinBERT analysis on latest {ticker} headlines  ·  Model: ProsusAI/finbert")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
    st.info(
        "⚡ First load downloads the FinBERT model (~500MB). Subsequent loads are instant.",
        icon="ℹ️",
    )
 
    with st.spinner("Running AI sentiment analysis on latest news..."):
        df_sent = analyze_sentiment(ticker)
        overall = get_overall_sentiment(df_sent)
 
    if df_sent.empty:
        show_empty_state(
            f"No news found for {ticker}. Try a different stock.",
            icon="📰"
        )
    else:
        col_donut, col_stats = st.columns([1, 1])
 
        with col_donut:
            st.plotly_chart(build_sentiment_donut(overall), use_container_width=True)
 
        with col_stats:
            st.markdown("<br>", unsafe_allow_html=True)
            label_color = {
                "positive": "#166534",
                "negative": "#991B1B",
                "neutral":  "#374151",
            }[overall["label"]]
            sign = "+" if overall["score"] >= 0 else ""
 
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E5E7EB;"
                f"border-top:3px solid #1B3A6B;border-radius:8px;padding:1.5rem;margin-bottom:12px'>"
                f"<div style='font-size:0.65rem;font-weight:700;letter-spacing:.1em;"
                f"text-transform:uppercase;color:#9CA3AF;margin-bottom:8px'>Overall Sentiment Score</div>"
                f"<div style='font-size:2.5rem;font-weight:500;font-family:JetBrains Mono,monospace;"
                f"color:{label_color};line-height:1'>{sign}{overall['score']}</div>"
                f"<div style='font-size:0.78rem;color:#9CA3AF;margin-top:6px'>"
                f"Based on {overall['count']} headlines</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
 
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Positive", f"{overall['positive']}%")
            with c2: st.metric("Neutral",  f"{overall['neutral']}%")
            with c3: st.metric("Negative", f"{overall['negative']}%")
 
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
        fig_bar = build_sentiment_bar_chart(df_sent, ticker)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
 
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("#### Latest Headlines")
 
        sentiment_styles = {
            "positive": ("#166534", "#F0FDF4", "#BBF7D0"),
            "negative": ("#991B1B", "#FEF2F2", "#FECACA"),
            "neutral":  ("#374151", "#F9FAFB", "#E5E7EB"),
        }
 
        for _, row in df_sent.iterrows():
            color, bg, border = sentiment_styles[row["sentiment"]]
            link_html = (
                f"<a href='{row['link']}' target='_blank' "
                f"style='color:#1B3A6B;font-size:0.72rem;text-decoration:none;"
                f"font-weight:500'>Read article →</a>"
            ) if row["link"] else ""
 
            st.markdown(
                f"<div style='background:{bg};border:1px solid {border};"
                f"border-left:3px solid {color};border-radius:6px;"
                f"padding:0.9rem 1rem;margin-bottom:8px'>"
                f"<div style='font-size:0.85rem;font-weight:500;color:#111827;"
                f"margin-bottom:6px;line-height:1.4;font-family:Inter,sans-serif'>"
                f"{row['title']}</div>"
                f"<div style='display:flex;align-items:center;gap:12px'>"
                f"<span style='font-size:0.7rem;color:#6B7280'>"
                f"{row['publisher']} · {row['published']}</span>"
                f"<span style='background:{bg};border:1px solid {border};"
                f"color:{color};font-size:0.65rem;font-weight:700;"
                f"padding:1px 7px;border-radius:20px;text-transform:uppercase;"
                f"letter-spacing:0.06em'>{row['sentiment']} {row['confidence']*100:.0f}%</span>"
                f"{link_html}</div></div>",
                unsafe_allow_html=True,
            )
 
        st.caption(
            f"Powered by FinBERT (ProsusAI)  ·  "
            f"{overall['count']} articles analysed  ·  Refreshes every 5 minutes"
        )
 
 
# ════════════════════════════════════════════════════════════════════
# TAB 5 — ANOMALY DETECTION
# ════════════════════════════════════════════════════════════════════
with tab5:
    from src.anomaly import (
        detect_anomalies, get_anomaly_summary,
        build_anomaly_price_chart,
        build_anomaly_score_chart,
        build_feature_importance_chart,
    )
 
    st.markdown("### Anomaly Detection")
    st.caption(f"Isolation Forest ML model detecting unusual price & volume activity  ·  {ticker}")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        st.info(
            "🤖 Isolation Forest trains on 7 engineered features: "
            "returns, volatility, volume spikes, price gaps and more. "
            "Points scoring below 0 are flagged as anomalies.",
            icon="ℹ️",
        )
    with col_ctrl2:
        contamination = st.slider(
            "Sensitivity (% flagged)",
            min_value=1, max_value=15, value=5, step=1,
            help="Higher = more anomalies flagged. Default 5% is recommended.",
        ) / 100
 
    with st.spinner("Training Isolation Forest model..."):
        df_anom = detect_anomalies(ticker, period_code, contamination)
        summary = get_anomaly_summary(df_anom)
 
    if df_anom.empty:
        show_error_card(
            f"Not enough data for {ticker}",
            "Need at least 30 data points. Try a longer time period."
        )
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("Total Bars",    summary["total"])
        with c2: st.metric("Anomalies",     summary["anomalies"])
        with c3: st.metric("Flagged %",     f"{summary['pct']}%")
        with c4: st.metric("Last Anomaly",  summary["last_anomaly"])
        with c5: st.metric("High Severity", summary["high"])
 
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
        sev1, sev2, sev3 = st.columns(3)
        sev_styles = [
            (summary["high"],   "#166534", "#F0FDF4", "#BBF7D0", "High Severity"),
            (summary["medium"], "#92400E", "#FFFBEB", "#FDE68A", "Medium Severity"),
            (summary["low"],    "#374151", "#F9FAFB", "#E5E7EB", "Low Severity"),
        ]
        for col, (val, color, bg, border, label) in zip([sev1, sev2, sev3], sev_styles):
            with col:
                st.markdown(
                    f"<div style='background:{bg};border:1px solid {border};"
                    f"border-left:3px solid {color};border-radius:8px;"
                    f"padding:1rem;text-align:center'>"
                    f"<div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;"
                    f"text-transform:uppercase;color:{color};margin-bottom:6px'>{label}</div>"
                    f"<div style='font-size:2rem;font-weight:500;"
                    f"font-family:JetBrains Mono,monospace;color:{color}'>{val}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
 
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
 
        st.plotly_chart(build_anomaly_price_chart(df_anom, ticker), use_container_width=True)
        st.plotly_chart(build_anomaly_score_chart(df_anom, ticker), use_container_width=True)
 
        col_feat1, col_feat2 = st.columns([1, 1])
        with col_feat1:
            st.plotly_chart(build_feature_importance_chart(df_anom, ticker), use_container_width=True)
        with col_feat2:
            st.markdown(
                "<div style='background:#FFFFFF;border:1px solid #E5E7EB;"
                "border-radius:8px;padding:1.25rem;height:100%'>"
                "<p style='font-size:0.65rem;font-weight:700;letter-spacing:.1em;"
                "text-transform:uppercase;color:#9CA3AF;margin:0 0 12px'>Feature Reference</p>"
                "<table style='width:100%;font-size:0.78rem;border-collapse:collapse'>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>return</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Daily % price change</td></tr>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>high_low_range</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Intraday price spread</td></tr>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>open_close</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Open to close move</td></tr>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>volume_change</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Volume % change</td></tr>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>volume_zscore</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Volume vs 20-day avg</td></tr>"
                "<tr style='border-bottom:1px solid #F3F4F6'>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>rolling_std</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>5-day return volatility</td></tr>"
                "<tr>"
                "<td style='padding:6px 0;color:#6B7280;font-family:JetBrains Mono,monospace'>gap</td>"
                "<td style='padding:6px 0;text-align:right;color:#374151'>Overnight price gap</td></tr>"
                "</table></div>",
                unsafe_allow_html=True
            )
 
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("#### Flagged Anomaly Events")
 
        anomaly_events = df_anom[df_anom["is_anomaly"]].copy()
        if anomaly_events.empty:
            st.info("No anomalies detected at current sensitivity level.")
        else:
            anomaly_events.index = anomaly_events.index.strftime("%Y-%m-%d")
            display_df = anomaly_events[[
                "open", "high", "low", "close",
                "volume", "anomaly_score", "severity"
            ]].copy()
            display_df.columns = ["Open", "High", "Low", "Close", "Volume", "Score", "Severity"]
            display_df["Close"]  = display_df["Close"].map("${:.2f}".format)
            display_df["Score"]  = display_df["Score"].map("{:.4f}".format)
            display_df["Volume"] = display_df["Volume"].map("{:,.0f}".format)
            st.dataframe(display_df, use_container_width=True)
 
        st.caption(
            f"Isolation Forest  ·  n_estimators=200  ·  "
            f"contamination={contamination:.0%}  ·  {summary['total']} bars analysed"
        )

# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("""
<div style='
    background: #FFFFFF;
    border-top: 1px solid #E5E7EB;
    margin: 3rem -2rem -3rem -2rem;
    padding: 1.5rem 2rem;
'>
    <div style='
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    '>
        <div style='display:flex;align-items:center;gap:12px'>
            <div style='
                background:#1B3A6B;border-radius:5px;
                width:26px;height:26px;display:flex;
                align-items:center;justify-content:center;
                font-size:0.8rem
            '>📈</div>
            <div>
                <div style='
                    font-size:0.78rem;font-weight:700;
                    color:#111827;font-family:Inter,sans-serif;
                    letter-spacing:-0.01em
                '>Stock Market Dashboard</div>
                <div style='
                    font-size:0.65rem;color:#9CA3AF;
                    font-family:Inter,sans-serif
                '>Real-time market data & AI analytics</div>
            </div>
        </div>

        <div style='display:flex;align-items:center;gap:24px;flex-wrap:wrap'>
            <div style='text-align:center'>
                <div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:#9CA3AF;margin-bottom:2px'>Charts</div>
                <div style='font-size:0.75rem;font-weight:500;color:#374151'>Plotly</div>
            </div>
            <div style='width:1px;height:24px;background:#E5E7EB'></div>
            <div style='text-align:center'>
                <div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:#9CA3AF;margin-bottom:2px'>Data</div>
                <div style='font-size:0.75rem;font-weight:500;color:#374151'>Yahoo Finance</div>
            </div>
            <div style='width:1px;height:24px;background:#E5E7EB'></div>
            <div style='text-align:center'>
                <div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:#9CA3AF;margin-bottom:2px'>AI Model</div>
                <div style='font-size:0.75rem;font-weight:500;color:#374151'>FinBERT</div>
            </div>
            <div style='width:1px;height:24px;background:#E5E7EB'></div>
            <div style='text-align:center'>
                <div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:#9CA3AF;margin-bottom:2px'>ML Model</div>
                <div style='font-size:0.75rem;font-weight:500;color:#374151'>Isolation Forest</div>
            </div>
            <div style='width:1px;height:24px;background:#E5E7EB'></div>
            <div style='text-align:center'>
                <div style='font-size:0.6rem;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:#9CA3AF;margin-bottom:2px'>Framework</div>
                <div style='font-size:0.75rem;font-weight:500;color:#374151'>Streamlit</div>
            </div>
        </div>

        <div style='text-align:right'>
            <div style='font-size:0.72rem;color:#6B7280;font-family:Inter,sans-serif'>
                Built by <span style='font-weight:600;color:#1B3A6B'>Vasundhara Shivankar</span>
            </div>
            <div style='font-size:0.65rem;color:#9CA3AF;margin-top:2px'>
                6-Month Python Developer Internship · Codec Technologies
            </div>
        </div>
    </div>

    <div style='
        margin-top:1rem;
        padding-top:1rem;
        border-top:1px solid #F3F4F6;
        display:flex;
        align-items:center;
        justify-content:space-between;
        flex-wrap:wrap;
        gap:8px;
    '>
        <div style='font-size:0.65rem;color:#9CA3AF;font-family:Inter,sans-serif'>
            Data refreshes every 60 seconds · Charts powered by Plotly · 
            AI analysis by FinBERT (ProsusAI) · Anomaly detection by Isolation Forest
        </div>
        <div style='font-size:0.65rem;color:#9CA3AF;font-family:Inter,sans-serif'>
            ⚠ For informational purposes only. Not financial advice.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)