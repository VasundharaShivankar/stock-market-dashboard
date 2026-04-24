# src/errors.py — Reusable Streamlit error/state UI components

import streamlit as st


def show_empty_state(message: str, icon: str = "📭"):
    """Centred empty state with icon and message."""
    st.markdown(
        f"""
        <div style='
            text-align  : center;
            padding     : 60px 20px;
            color       : #8B949E;
        '>
            <div style='font-size:3rem'>{icon}</div>
            <div style='font-size:1rem;margin-top:12px'>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_error_card(title: str, detail: str = ""):
    """Red-bordered error card."""
    st.markdown(
        f"""
        <div style='
            background : #1a0a0a;
            border     : 1px solid #EF5350;
            border-radius: 8px;
            padding    : 16px 20px;
            color      : #EF5350;
            margin     : 8px 0;
        '>
            <strong>⚠ {title}</strong>
            {"<div style='color:#8B949E;font-size:0.85rem;margin-top:6px'>" + detail + "</div>" if detail else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_warning_card(message: str):
    """Amber warning card."""
    st.markdown(
        f"""
        <div style='
            background : #1a1400;
            border     : 1px solid #F59E0B;
            border-radius: 8px;
            padding    : 12px 16px;
            color      : #F59E0B;
            font-size  : 0.9rem;
            margin     : 8px 0;
        '>
            ⚡ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_success_card(message: str):
    """Green success card."""
    st.markdown(
        f"""
        <div style='
            background : #0a1a0f;
            border     : 1px solid #26A69A;
            border-radius: 8px;
            padding    : 12px 16px;
            color      : #26A69A;
            font-size  : 0.9rem;
            margin     : 8px 0;
        '>
            ✓ {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_loading_skeleton():
    """Placeholder while chart data loads."""
    st.markdown(
        """
        <div style='
            background    : #1E2329;
            border-radius : 8px;
            height        : 400px;
            width         : 100%;
            margin        : 8px 0;
            display       : flex;
            align-items   : center;
            justify-content: center;
            color         : #3A3F4A;
            font-size     : 0.9rem;
        '>
            Loading chart data...
        </div>
        """,
        unsafe_allow_html=True,
    )


def validate_and_show_error(ticker: str, df) -> bool:
    """
    Returns True if data is valid and ready to use.
    Shows appropriate error UI and returns False otherwise.
    """
    if df is None:
        show_error_card(
            f"Failed to fetch data for {ticker}",
            "Yahoo Finance did not return a response. Try again in a few seconds."
        )
        return False

    if hasattr(df, "empty") and df.empty:
        show_error_card(
            f"No data available for {ticker}",
            "This may be a delisted stock, invalid symbol, or a temporary "
            "Yahoo Finance outage. Try a different period or ticker."
        )
        return False

    if hasattr(df, "__len__") and len(df) < 5:
        show_warning_card(
            f"Very limited data for {ticker} ({len(df)} rows). "
            "Some indicators may not display correctly."
        )
        return True

    return True