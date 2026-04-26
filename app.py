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
/* Dark background */
.stApp { background-color: #0E1117; }

/* Metric cards */
[data-testid="metric-container"] {
    background    : #1E2329;
    border        : 1px solid #2A2E39;
    border-radius : 8px;
    padding       : 12px 16px;
}

/* Positive/negative delta colors */
[data-testid="stMetricDelta"] svg { display: none; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #161B22; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiselect label,
[data-testid="stSidebar"] .stCheckbox label { color: #C9D1D9; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap              : 4px;
    background-color : #161B22;
    border-radius    : 8px;
    padding          : 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color : transparent;
    border-radius    : 6px;
    color            : #8B949E;
    padding          : 6px 18px;
}
.stTabs [aria-selected="true"] {
    background-color : #21262D;
    color            : #E6EDF3;
}

/* Price header */
.price-header {
    font-size   : 2.4rem;
    font-weight : 700;
    color       : #E6EDF3;
    line-height : 1;
}
.price-change-pos { color: #26A69A; font-size: 1.1rem; }
.price-change-neg { color: #EF5350; font-size: 1.1rem; }

/* Ticker badge */
.ticker-badge {
    display          : inline-block;
    background-color : #21262D;
    color            : #58A6FF;
    border           : 1px solid #30363D;
    border-radius    : 6px;
    padding          : 2px 10px;
    font-size        : 0.85rem;
    font-weight      : 600;
    margin-bottom    : 4px;
}

/* Divider */
.section-divider {
    border     : none;
    border-top : 1px solid #21262D;
    margin     : 16px 0;
}

/* Hide streamlit branding */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
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
    st.markdown(f"## {APP_ICON} {APP_TITLE}")
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
        add_clicked = st.button("Add", width='stretch')

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
                width='stretch',
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
tab1, tab2, tab3 = st.tabs(["📊 Chart", "🔁 Compare", "ℹ️ Info"])


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
            f"<div style='color:#8B949E;font-size:0.85rem'>"
            f"{info_data['name']}</div>",
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
        st.plotly_chart(fig_price, width='stretch')

        # RSI
        if show_rsi:
            fig_rsi = build_rsi_chart(df, ticker)
            st.plotly_chart(fig_rsi, width='stretch')

        # MACD
        if show_macd:
            fig_macd = build_macd_chart(df, ticker)
            st.plotly_chart(fig_macd, width='stretch')

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
            st.plotly_chart(fig_cmp, width='stretch')

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
                    width='stretch',
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