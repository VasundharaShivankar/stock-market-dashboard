# app.py — Main Streamlit entry point

import streamlit as st
import time
from config import (
    APP_TITLE, APP_ICON, DEFAULT_TICKERS,
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

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title = APP_TITLE,
    page_icon  = APP_ICON,
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: #F7F8FA !important;
    color: #0A0F1E !important;
}

/* ── Top accent bar ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0033A0 0%, #0057D8 50%, #00A3E0 100%);
    z-index: 9999;
}

/* ── Main container ── */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1440px !important;
    background: #F7F8FA;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E6ED !important;
}
[data-testid="stSidebar"] > div {
    padding-top: 1.5rem !important;
}
[data-testid="stSidebar"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #6B7A99 !important;
}
[data-testid="stSidebar"] .stMarkdown h4 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #6B7A99 !important;
}

/* ── Sidebar inputs ── */
[data-testid="stSidebar"] input {
    background: #F7F8FA !important;
    border: 1px solid #D1D9E6 !important;
    border-radius: 6px !important;
    color: #0A0F1E !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stSidebar"] input:focus {
    border-color: #0033A0 !important;
    box-shadow: 0 0 0 3px rgba(0,51,160,0.08) !important;
    background: #FFFFFF !important;
}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton button {
    background: #FFFFFF !important;
    border: 1px solid #D1D9E6 !important;
    border-radius: 6px !important;
    color: #0A0F1E !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    padding: 0.35rem 0.75rem !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #EEF2FF !important;
    border-color: #0033A0 !important;
    color: #0033A0 !important;
}

/* ── Add button ── */
[data-testid="stSidebar"] .stButton:first-of-type button {
    background: #0033A0 !important;
    border-color: #0033A0 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton:first-of-type button:hover {
    background: #002280 !important;
    border-color: #002280 !important;
    color: #FFFFFF !important;
}

/* ── Selectbox ── */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #F7F8FA !important;
    border: 1px solid #D1D9E6 !important;
    border-radius: 6px !important;
    color: #0A0F1E !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
}

/* ── Radio ── */
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    color: #0A0F1E !important;
}

/* ── Checkboxes ── */
[data-testid="stSidebar"] .stCheckbox label {
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    color: #3D4F6B !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E6ED !important;
    border-top: 3px solid #0033A0 !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
    transition: box-shadow 0.15s ease;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 16px rgba(0,51,160,0.08) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #6B7A99 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.3rem !important;
    font-weight: 500 !important;
    color: #0A0F1E !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid #E2E6ED !important;
    padding: 0 !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    color: #6B7A99 !important;
    padding: 10px 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    transition: color 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0033A0 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #0033A0 !important;
    border-bottom: 2px solid #0033A0 !important;
    background: transparent !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── Price display ── */
.price-header {
    font-family: 'DM Mono', monospace;
    font-size: 2.2rem;
    font-weight: 500;
    color: #0A0F1E;
    line-height: 1;
    letter-spacing: -0.02em;
}
.price-change-pos {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    color: #15803D;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 4px;
    padding: 2px 8px;
    margin-top: 6px;
}
.price-change-neg {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    color: #B91C1C;
    background: #FFF1F1;
    border: 1px solid #FECACA;
    border-radius: 4px;
    padding: 2px 8px;
    margin-top: 6px;
}

/* ── Ticker badge ── */
.ticker-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0033A0;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 3px 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}

/* ── Company name ── */
.company-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #0A0F1E;
    margin: 0;
}

/* ── Section divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #E2E6ED;
    margin: 1.5rem 0;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E6ED !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    overflow: hidden !important;
}

/* ── Info / warning / error boxes ── */
.stAlert {
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    border-left-width: 4px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F7F8FA; }
::-webkit-scrollbar-thumb {
    background: #D1D9E6;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: #A0AEC0; }

/* ── App logo ── */
.app-logo {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #0A0F1E;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2px;
}
.app-tagline {
    font-size: 0.65rem;
    color: #6B7A99;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 1.25rem;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] p {
    font-family: 'DM Sans', sans-serif !important;
    color: #6B7A99 !important;
    font-size: 0.72rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #0033A0 !important;
}

/* ── Responsive: stack on mobile ── */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 1rem 2rem !important;
    }
    .price-header {
        font-size: 1.6rem !important;
    }
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
    }
}

/* ── Section headers ── */
.section-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6B7A99;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #E2E6ED;
    margin-bottom: 0.75rem;
}

/* ── Status pill ── */
.status-live {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #15803D;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 2px 8px;
}
.status-live::before {
    content: '';
    width: 5px;
    height: 5px;
    background: #15803D;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Hide Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Defaults ───────────────────────────────────────────────────

if "tickers"      not in st.session_state:
    st.session_state.tickers      = ["AAPL", "MSFT"]
if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = "AAPL"
if "last_refresh"  not in st.session_state:
    st.session_state.last_refresh  = time.time()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f"<div class='app-logo'>{APP_ICON} {APP_TITLE}</div>"
        f"<div class='app-tagline'>Market Intelligence Platform</div>"
        f"<div style='margin-bottom:1rem'><span class='status-live'>Live</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Add ticker ────────────────────────────────────────────────────────────
    st.markdown("#### Add Stock")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_ticker = st.text_input(
            "Ticker symbol", placeholder="e.g. TSLA",
            label_visibility="collapsed"
        ).upper().strip()
    with col2:
        add_clicked = st.button("Add", use_container_width=True)

    if add_clicked and new_ticker:
        if new_ticker in st.session_state.tickers:
            st.warning(f"{new_ticker} already added.")
        else:
            with st.spinner(f"Validating {new_ticker}..."):
                if validate_ticker(new_ticker):
                    st.session_state.tickers.append(new_ticker)
                    st.session_state.active_ticker = new_ticker
                    st.success(f"✓ {new_ticker} added!")
                    st.rerun()
                else:
                    st.error(f"'{new_ticker}' not found.")

    # ── Watchlist ─────────────────────────────────────────────────────────────
    st.markdown("#### Watchlist")
    for ticker in list(st.session_state.tickers):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            active = ticker == st.session_state.active_ticker
            if st.button(
                f"{'▶ ' if active else '   '}{ticker}",
                key=f"btn_{ticker}",
                use_container_width=True,
            ):
                st.session_state.active_ticker = ticker
                st.rerun()
        with col_b:
            if st.button("✕", key=f"del_{ticker}", help=f"Remove {ticker}"):
                st.session_state.tickers.remove(ticker)
                if st.session_state.active_ticker == ticker:
                    st.session_state.active_ticker = (
                        st.session_state.tickers[0]
                        if st.session_state.tickers else ""
                    )
                st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Chart settings ────────────────────────────────────────────────────────
    st.markdown("#### Chart Settings")

    period = st.selectbox(
        "Time period",
        options=list(TIME_PERIODS.keys()),
        index=2,
    )
    period_code = TIME_PERIODS[period]

    chart_type = st.radio(
        "Chart type",
        options=["Candlestick", "Line"],
        horizontal=True,
    )

    st.markdown("**Overlays**")
    show_sma20  = st.checkbox("SMA 20",         value=True)
    show_sma50  = st.checkbox("SMA 50",         value=True)
    show_ema20  = st.checkbox("EMA 20",         value=False)
    show_ema50  = st.checkbox("EMA 50",         value=False)
    show_bb     = st.checkbox("Bollinger Bands",value=False)
    show_volume = st.checkbox("Volume",         value=True)

    st.markdown("**Oscillators**")
    show_rsi  = st.checkbox("RSI",  value=True)
    show_macd = st.checkbox("MACD", value=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── Auto refresh ──────────────────────────────────────────────────────────
    st.markdown("#### Auto Refresh")
    refresh_label = st.selectbox(
        "Interval",
        options=list(REFRESH_INTERVALS.keys()),
        index=0,
    )
    refresh_secs = REFRESH_INTERVALS[refresh_label]

    if refresh_secs > 0:
        elapsed = time.time() - st.session_state.last_refresh
        remaining = max(0, refresh_secs - elapsed)
        st.caption(f"Next refresh in {int(remaining)}s")
        if elapsed >= refresh_secs:
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.caption("Data via Yahoo Finance · yfinance 1.3.0")


# ─── Main Area ────────────────────────────────────────────────────────────────

ticker = st.session_state.active_ticker

if not ticker:
    st.info("Add a stock ticker from the sidebar to get started.")
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Chart", "🔁 Compare", "ℹ️ Info", "🧠 Sentiment", "🚨 Anomaly"])


# ════════════════════════════════════════════════════════════════════
# TAB 1 — CHART
# ════════════════════════════════════════════════════════════════════
with tab1:

    # Live price header
    price_data = fetch_live_price(ticker)
    info_data  = fetch_stock_info(ticker)

    col_name, col_price, col_m1, col_m2, col_m3, col_m4 = st.columns([2,2,1,1,1,1])

    with col_name:
        st.markdown(f"<div class='ticker-badge'>{ticker}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='company-name'>{info_data['name']}</div>",
            unsafe_allow_html=True
        )

    with col_price:
        sign  = "+" if price_data["change"] >= 0 else ""
        color = "price-change-pos" if price_data["change"] >= 0 else "price-change-neg"
        st.markdown(
            f"<div class='price-header'>${price_data['price']:,.2f}</div>"
            f"<div class='{color}'>"
            f"{sign}{price_data['change']:.2f} "
            f"({sign}{price_data['pct']:.2f}%)"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_m1:
        st.metric("Day High",  f"${price_data['high']:,.2f}")
    with col_m2:
        st.metric("Day Low",   f"${price_data['low']:,.2f}")
    with col_m3:
        st.metric("Prev Close",f"${price_data['prev']:,.2f}")
    with col_m4:
        st.metric("Volume",    format_volume(price_data["volume"]))

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Build indicator list from checkboxes
    selected_indicators = []
    if show_sma20: selected_indicators.append("SMA 20")
    if show_sma50: selected_indicators.append("SMA 50")
    if show_ema20: selected_indicators.append("EMA 20")
    if show_ema50: selected_indicators.append("EMA 50")

    # Fetch data and render charts
    with st.spinner(f"Loading {ticker} · {period}..."):
        df = fetch_stock_history(ticker, period_code)

    if df.empty:
        st.error(f"No data returned for **{ticker}**. Try a different period.")
    else:
        # Price chart
        fig_price = build_price_chart(
            df, ticker, chart_type,
            indicators   = selected_indicators,
            show_volume  = show_volume,
            show_bollinger = show_bb,
        )
        st.plotly_chart(fig_price, use_container_width=True)

        # RSI
        if show_rsi:
            fig_rsi = build_rsi_chart(df, ticker)
            st.plotly_chart(fig_rsi, use_container_width=True)

        # MACD
        if show_macd:
            fig_macd = build_macd_chart(df, ticker)
            st.plotly_chart(fig_macd, use_container_width=True)

    # Last updated timestamp
    st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")


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
        st.info("Select at least 2 stocks to compare.")
    else:
        with st.spinner("Loading comparison data..."):
            compare_data = fetch_multiple_tickers(compare_tickers, period_code)

        if compare_data:
            fig_cmp = build_comparison_chart(compare_data)
            st.plotly_chart(fig_cmp, use_container_width=True)

            # Stats table
            st.markdown("#### Period Summary")
            rows = []
            for t, d in compare_data.items():
                if d.empty:
                    continue
                start  = d["close"].iloc[0]
                end    = d["close"].iloc[-1]
                ret    = ((end - start) / start) * 100
                hi     = d["high"].max()
                lo     = d["low"].min()
                rows.append({
                    "Ticker":       t,
                    "Start":        f"${start:.2f}",
                    "End":          f"${end:.2f}",
                    "Return":       f"{ret:+.2f}%",
                    "Period High":  f"${hi:.2f}",
                    "Period Low":   f"${lo:.2f}",
                })
            if rows:
                import pandas as pd
                st.dataframe(
                    pd.DataFrame(rows).set_index("Ticker"),
                    use_container_width=True,
                )


# ════════════════════════════════════════════════════════════════════
# TAB 3 — INFO
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"### {info_data['name']}")
    st.markdown(f"`{ticker}` · {info_data['exchange']} · {info_data['currency']}")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1:
        st.metric("Market Cap",  format_market_cap(info_data["market_cap"]))
    with col_i2:
        pe = info_data["pe_ratio"]
        st.metric("P/E Ratio",   f"{pe:.2f}" if pe else "N/A")
    with col_i3:
        hi = info_data["52w_high"]
        st.metric("52W High",    f"${hi:.2f}" if hi else "N/A")
    with col_i4:
        lo = info_data["52w_low"]
        st.metric("52W Low",     f"${lo:.2f}" if lo else "N/A")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_i5, col_i6 = st.columns(2)
    with col_i5:
        st.markdown(f"**Sector:** {info_data['sector']}")
        st.markdown(f"**Industry:** {info_data['industry']}")
        div = info_data["dividend"]
        st.markdown(f"**Dividend Yield:** {f'{div*100:.2f}%' if div else 'N/A'}")
    with col_i6:
        st.markdown(f"**Avg Volume:** {format_volume(info_data['avg_volume'])}")
        if info_data["website"]:
            st.markdown(f"**Website:** [{info_data['website']}]({info_data['website']})")

    if info_data["description"]:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("**About**")
        st.markdown(
            f"<div style='color:#8B949E;font-size:0.9rem;line-height:1.6'>"
            f"{info_data['description'][:800]}...</div>",
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

    st.markdown("### 🧠 AI News Sentiment")
    st.caption(
        f"FinBERT analysis on latest {ticker} headlines · "
        "Model: ProsusAI/finbert"
    )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # Warn that first load downloads the model
    st.info(
        "⚡ First load downloads the FinBERT model (~500MB). "
        "Subsequent loads are instant.",
        icon="ℹ️",
    )

    with st.spinner("Running AI sentiment analysis on latest news..."):
        df_sent   = analyze_sentiment(ticker)
        overall   = get_overall_sentiment(df_sent)

    if df_sent.empty:
        from src.errors import show_empty_state
        show_empty_state(
            f"No news found for {ticker}. Try a different stock.",
            icon="📰"
        )
    else:
        # ── Overall metrics row ───────────────────────────────────────
        col_donut, col_stats = st.columns([1, 1])

        with col_donut:
            fig_donut = build_sentiment_donut(overall)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_stats:
            st.markdown("<br>", unsafe_allow_html=True)

            label_color = {
                "positive": "#10B981",
                "negative": "#EF4444",
                "neutral":  "#6B7280",
            }[overall["label"]]

            sign = "+" if overall["score"] >= 0 else ""

            st.markdown(
                f"""
                <div style='
                    background: rgba(255,255,255,0.02);
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 14px;
                    padding: 1.5rem;
                    margin-bottom: 12px;
                '>
                    <div style='font-size:0.72rem;letter-spacing:0.06em;
                                text-transform:uppercase;color:#5A6478;
                                font-family:Sora,sans-serif;margin-bottom:8px'>
                        Overall Sentiment Score
                    </div>
                    <div style='font-size:2.8rem;font-weight:500;
                                font-family:JetBrains Mono,monospace;
                                color:{label_color};line-height:1'>
                        {sign}{overall["score"]}
                    </div>
                    <div style='font-size:0.8rem;color:#5A6478;margin-top:6px'>
                        Based on {overall["count"]} headlines
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Positive", f"{overall['positive']}%")
            with c2:
                st.metric("Neutral",  f"{overall['neutral']}%")
            with c3:
                st.metric("Negative", f"{overall['negative']}%")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # ── Per-headline bar chart ────────────────────────────────────
        fig_bar = build_sentiment_bar_chart(df_sent, ticker)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        # ── News cards ────────────────────────────────────────────────
        st.markdown("#### Latest Headlines")

        sentiment_colors = {
            "positive": ("#10B981", "rgba(16,185,129,0.08)", "rgba(16,185,129,0.2)"),
            "negative": ("#EF4444", "rgba(239,68,68,0.08)",  "rgba(239,68,68,0.2)"),
            "neutral":  ("#6B7280", "rgba(107,114,128,0.08)","rgba(107,114,128,0.2)"),
        }

        for _, row in df_sent.iterrows():
            color, bg, border = sentiment_colors[row["sentiment"]]
            link_html = (
                f"<a href='{row['link']}' target='_blank' "
                f"style='color:{color};font-size:0.75rem;text-decoration:none;'>"
                f"Read article →</a>"
            ) if row["link"] else ""

            st.markdown(
                f"""
                <div style='
                    background: {bg};
                    border: 1px solid {border};
                    border-left: 3px solid {color};
                    border-radius: 10px;
                    padding: 0.9rem 1.1rem;
                    margin-bottom: 8px;
                '>
                    <div style='font-size:0.88rem;font-weight:500;
                                color:#C4CDD8;margin-bottom:4px;
                                font-family:Sora,sans-serif;line-height:1.4'>
                        {row["title"]}
                    </div>
                    <div style='display:flex;align-items:center;
                                gap:12px;margin-top:6px'>
                        <span style='font-size:0.72rem;color:#5A6478'>
                            {row["publisher"]} · {row["published"]}
                        </span>
                        <span style='
                            background:{bg};border:1px solid {border};
                            color:{color};font-size:0.68rem;font-weight:600;
                            padding:2px 8px;border-radius:20px;
                            text-transform:uppercase;letter-spacing:0.05em'>
                            {row["sentiment"]} {row["confidence"]*100:.0f}%
                        </span>
                        {link_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            f"Powered by FinBERT (ProsusAI) · "
            f"{overall['count']} articles analysed · "
            f"Refreshes every 5 minutes"
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

    st.markdown("### 🚨 Anomaly Detection")
    st.caption(f"Isolation Forest ML model · {ticker}")
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        st.info("🤖 Isolation Forest trains on 7 engineered features: returns, volatility, volume spikes, price gaps and more.")
    with col_ctrl2:
        contamination = st.slider("Sensitivity (% flagged)", 1, 15, 5, 1) / 100

    with st.spinner("Training Isolation Forest model..."):
        df_anom = detect_anomalies(ticker, period_code, contamination)
        summary = get_anomaly_summary(df_anom)

    if df_anom.empty:
        st.error(f"Not enough data for {ticker}. Need 30+ bars. Try a longer period.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.metric("Total Bars",    summary["total"])
        with c2: st.metric("Anomalies",     summary["anomalies"])
        with c3: st.metric("Flagged %",     f"{summary['pct']}%")
        with c4: st.metric("Last Anomaly",  summary["last_anomaly"])
        with c5: st.metric("High Severity", summary["high"])

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        sev1, sev2, sev3 = st.columns(3)
        with sev1:
            st.markdown(f"""<div style='background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);
                border-left:3px solid #EF4444;border-radius:10px;padding:1rem;text-align:center'>
                <div style='font-size:0.72rem;text-transform:uppercase;color:#5A6478'>High Severity</div>
                <div style='font-size:2rem;font-weight:500;font-family:JetBrains Mono,monospace;color:#EF4444'>{summary['high']}</div>
                </div>""", unsafe_allow_html=True)
        with sev2:
            st.markdown(f"""<div style='background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);
                border-left:3px solid #F59E0B;border-radius:10px;padding:1rem;text-align:center'>
                <div style='font-size:0.72rem;text-transform:uppercase;color:#5A6478'>Medium Severity</div>
                <div style='font-size:2rem;font-weight:500;font-family:JetBrains Mono,monospace;color:#F59E0B'>{summary['medium']}</div>
                </div>""", unsafe_allow_html=True)
        with sev3:
            st.markdown(f"""<div style='background:rgba(107,114,128,0.08);border:1px solid rgba(107,114,128,0.25);
                border-left:3px solid #6B7280;border-radius:10px;padding:1rem;text-align:center'>
                <div style='font-size:0.72rem;text-transform:uppercase;color:#5A6478'>Low Severity</div>
                <div style='font-size:2rem;font-weight:500;font-family:JetBrains Mono,monospace;color:#6B7280'>{summary['low']}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        st.plotly_chart(build_anomaly_price_chart(df_anom, ticker), use_container_width=True)
        st.plotly_chart(build_anomaly_score_chart(df_anom, ticker), use_container_width=True)

        col_feat1, col_feat2 = st.columns([1, 1])
        with col_feat1:
            st.plotly_chart(build_feature_importance_chart(df_anom, ticker), use_container_width=True)
        with col_feat2:
            st.markdown("#### What each feature means")
            st.markdown("""
| Feature | Description |
|---|---|
| `return` | Daily % price change |
| `high_low_range` | Intraday price spread |
| `open_close` | Open to close move |
| `volume_change` | Volume % change |
| `volume_zscore` | Volume vs 20-day average |
| `rolling_std` | 5-day return volatility |
| `gap` | Overnight price gap |
""")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("#### Flagged Anomaly Events")

        anomaly_events = df_anom[df_anom["is_anomaly"]].copy()
        if anomaly_events.empty:
            st.info("No anomalies detected at current sensitivity level.")
        else:
            anomaly_events.index = anomaly_events.index.strftime("%Y-%m-%d")
            display_df = anomaly_events[["open","high","low","close","volume","anomaly_score","severity"]].copy()
            display_df.columns = ["Open","High","Low","Close","Volume","Score","Severity"]
            display_df["Close"] = display_df["Close"].map("${:.2f}".format)
            display_df["Score"] = display_df["Score"].map("{:.4f}".format)
            display_df["Volume"] = display_df["Volume"].map("{:,.0f}".format)
            st.dataframe(display_df, use_container_width=True)

        st.caption(f"Isolation Forest · n_estimators=200 · contamination={contamination:.0%} · {summary['total']} bars")