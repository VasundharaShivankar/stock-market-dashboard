# src/sentiment.py — AI sentiment analysis for stock news

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# ─── Load model (cached so it only downloads once) ────────────────────────────

@st.cache_resource
def load_sentiment_model():
    """
    Load FinBERT — a BERT model fine-tuned specifically on financial text.
    Much more accurate than general sentiment models for stock news.
    Cached as a resource so it loads once and stays in memory.
    """
    try:
        from transformers import pipeline
        model = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            top_k=None,
        )
        return model
    except Exception as e:
        st.error(f"Failed to load sentiment model: {e}")
        return None


# ─── Fetch news ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_news(ticker: str) -> list:
    """
    Fetch latest news headlines for a ticker via yfinance.
    Returns list of dicts with title, publisher, link, published_at.
    """
    try:
        t     = yf.Ticker(ticker)
        news  = t.news or []
        items = []

        for article in news[:15]:
            content = article.get("content", {})

            # yfinance 1.3.0 returns nested content dict
            title = (
                content.get("title")
                or article.get("title")
                or ""
            )
            publisher = (
                content.get("provider", {}).get("displayName")
                or article.get("publisher")
                or "Unknown"
            )
            link = (
                content.get("canonicalUrl", {}).get("url")
                or article.get("link")
                or ""
            )
            pub_time = (
                content.get("pubDate")
                or article.get("providerPublishTime")
                or None
            )

            if not title:
                continue

            # Parse published time
            if isinstance(pub_time, str):
                try:
                    published = datetime.fromisoformat(
                        pub_time.replace("Z", "+00:00")
                    ).strftime("%b %d, %Y")
                except Exception:
                    published = pub_time[:10] if pub_time else "N/A"
            elif isinstance(pub_time, (int, float)):
                published = datetime.fromtimestamp(pub_time).strftime("%b %d, %Y")
            else:
                published = "N/A"

            items.append({
                "title":     title,
                "publisher": publisher,
                "link":      link,
                "published": published,
            })

        return items

    except Exception as e:
        st.error(f"Error fetching news for {ticker}: {e}")
        return []


# ─── Run sentiment analysis ───────────────────────────────────────────────────

@st.cache_data(ttl=300)
def analyze_sentiment(ticker: str) -> pd.DataFrame:
    """
    Runs FinBERT on each news headline.
    Returns a DataFrame with sentiment scores per article.
    """
    news  = fetch_news(ticker)
    if not news:
        return pd.DataFrame()

    model = load_sentiment_model()
    if model is None:
        return pd.DataFrame()

    rows = []
    for article in news:
        title = article["title"]
        try:
            # FinBERT returns scores for positive/negative/neutral
            results = model(title[:512])[0]
            scores  = {r["label"].lower(): round(r["score"], 4) for r in results}

            positive = scores.get("positive", 0)
            negative = scores.get("negative", 0)
            neutral  = scores.get("neutral",  0)

            # Dominant sentiment
            dominant = max(scores, key=scores.get)
            confidence = scores[dominant]

            rows.append({
                "title":      title,
                "publisher":  article["publisher"],
                "published":  article["published"],
                "link":       article["link"],
                "positive":   positive,
                "negative":   negative,
                "neutral":    neutral,
                "sentiment":  dominant,
                "confidence": confidence,
            })
        except Exception:
            continue

    return pd.DataFrame(rows)


# ─── Aggregate sentiment ──────────────────────────────────────────────────────

def get_overall_sentiment(df: pd.DataFrame) -> dict:
    """
    Compute weighted average sentiment across all headlines.
    Returns dict with scores and overall label.
    """
    if df.empty:
        return {
            "positive": 0, "negative": 0, "neutral": 0,
            "label": "neutral", "score": 0, "count": 0
        }

    avg_pos = df["positive"].mean()
    avg_neg = df["negative"].mean()
    avg_neu = df["neutral"].mean()

    scores = {"positive": avg_pos, "negative": avg_neg, "neutral": avg_neu}
    label  = max(scores, key=scores.get)

    # Sentiment score: +1 fully positive, -1 fully negative
    score  = round((avg_pos - avg_neg) * 100, 1)

    return {
        "positive": round(avg_pos * 100, 1),
        "negative": round(avg_neg * 100, 1),
        "neutral":  round(avg_neu * 100, 1),
        "label":    label,
        "score":    score,
        "count":    len(df),
    }


# ─── Chart builders ───────────────────────────────────────────────────────────

def build_sentiment_bar_chart(df: pd.DataFrame, ticker: str):
    """Horizontal bar chart showing sentiment per headline."""
    import plotly.graph_objects as go

    if df.empty:
        return None

    colors = {
        "positive": "#10B981",
        "negative": "#EF4444",
        "neutral":  "#6B7280",
    }

    short_titles = [t[:55] + "…" if len(t) > 55 else t for t in df["title"]]
    color_list   = [colors[s] for s in df["sentiment"]]

    fig = go.Figure(go.Bar(
        x           = df["confidence"] * 100,
        y           = short_titles,
        orientation = "h",
        marker_color= color_list,
        text        = [f"{s.capitalize()} {c*100:.0f}%"
                       for s, c in zip(df["sentiment"], df["confidence"])],
        textposition= "inside",
        insidetextanchor = "start",
        textfont    = dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Sentiment: %{text}<br>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        paper_bgcolor = "#080C14",
        plot_bgcolor  = "#080C14",
        font          = dict(color="#8B97A8", size=11),
        height        = max(300, len(df) * 42),
        margin        = dict(l=10, r=20, t=30, b=10),
        xaxis         = dict(
            range      = [0, 100],
            ticksuffix = "%",
            gridcolor  = "#1A2030",
            title      = "Confidence",
        ),
        yaxis = dict(
            gridcolor  = "rgba(0,0,0,0)",
            tickfont   = dict(size=10, color="#8B97A8"),
            automargin = True,
        ),
        title = dict(
            text = f"{ticker} — News Sentiment",
            x    = 0.01,
            font = dict(size=14, color="#C4CDD8"),
        ),
    )
    return fig


def build_sentiment_donut(overall: dict):
    """Donut chart showing overall sentiment breakdown."""
    import plotly.graph_objects as go

    fig = go.Figure(go.Pie(
        labels    = ["Positive", "Neutral", "Negative"],
        values    = [overall["positive"], overall["neutral"], overall["negative"]],
        hole      = 0.72,
        marker    = dict(colors=["#10B981", "#6B7280", "#EF4444"]),
        textinfo  = "none",
        hovertemplate = "%{label}: %{value:.1f}%<extra></extra>",
    ))

    label_color = {
        "positive": "#10B981",
        "negative": "#EF4444",
        "neutral":  "#6B7280",
    }[overall["label"]]

    sign = "+" if overall["score"] >= 0 else ""

    fig.add_annotation(
        text      = f"<b>{sign}{overall['score']}</b>",
        x=0.5, y=0.55,
        font      = dict(size=28, color=label_color, family="JetBrains Mono"),
        showarrow = False,
        xref="paper", yref="paper",
    )
    fig.add_annotation(
        text      = overall["label"].upper(),
        x=0.5, y=0.38,
        font      = dict(size=11, color=label_color, family="Sora"),
        showarrow = False,
        xref="paper", yref="paper",
    )

    fig.update_layout(
        paper_bgcolor = "#080C14",
        plot_bgcolor  = "#080C14",
        showlegend    = True,
        legend        = dict(
            orientation = "h",
            x=0.5, xanchor="center",
            y=-0.05,
            font=dict(color="#8B97A8", size=11),
        ),
        margin = dict(l=10, r=10, t=10, b=10),
        height = 260,
    )
    return fig