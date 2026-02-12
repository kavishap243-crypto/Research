from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from .dashboard_data import (
    earnings_rows,
    flatten_news,
    flatten_portfolio_news,
    flatten_sector_news,
    portfolio_rows,
)
from .main import sample_portfolio
from .service import ResearchFilterService

REFRESH_SECONDS = 300


def _filter_rows(rows: list[dict[str, str]], *, sectors: set[str], tickers: set[str], query: str) -> list[dict[str, str]]:
    query_lower = query.lower().strip()
    out: list[dict[str, str]] = []
    for row in rows:
        if sectors and row.get("sector", "") not in sectors:
            continue
        if tickers and row.get("ticker", "") not in tickers:
            continue
        haystack = f"{row.get('title', '')} {row.get('source', '')} {row.get('categories', '')}".lower()
        if query_lower and query_lower not in haystack:
            continue
        out.append(row)
    return out


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def load_dashboard_data() -> dict:
    service = ResearchFilterService()
    portfolio = sample_portfolio()
    sectors = sorted({p.sector for p in portfolio})

    macro_news = service.fetch_macro_news()
    sector_news = service.fetch_sector_news(sectors)
    portfolio_news = service.fetch_portfolio_news(portfolio)
    compatibility = service.compute_sector_compatibility(portfolio, sector_news)

    transcript_snippets = {
        stock.ticker: [
            f"{stock.company_name} management highlighted demand trends and margin discipline.",
            f"Analysts asked about growth visibility, capex, and risk controls for {stock.ticker}.",
        ]
        for stock in portfolio
    }
    earnings_reports = service.generate_earnings_reports(portfolio, transcript_snippets, quarter="Q3 FY26")

    return {
        "loaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "portfolio": portfolio,
        "macro_rows": flatten_news(macro_news),
        "sector_rows": flatten_sector_news(sector_news),
        "portfolio_rows": flatten_portfolio_news(portfolio_news),
        "holdings_rows": portfolio_rows(portfolio),
        "compatibility": compatibility,
        "earnings_rows": earnings_rows(earnings_reports),
    }


def main() -> None:
    st.set_page_config(page_title="Stock Research Live Dashboard", layout="wide")
    st.title("📈 Stock Research & Filter Live Dashboard")
    st.caption("Auto-refresh interval: every 5 minutes (300 seconds).")

    st_autorefresh(interval=REFRESH_SECONDS * 1000, key="dashboard-refresh")

    data = load_dashboard_data()

    left, right = st.columns([2, 1])
    with left:
        st.write(f"Last refreshed: **{data['loaded_at']}**")
    with right:
        if st.button("Refresh now"):
            st.cache_data.clear()
            st.rerun()

    holdings = data["holdings_rows"]
    all_sectors = sorted({h["sector"] for h in holdings})
    all_tickers = sorted({h["ticker"] for h in holdings})

    with st.sidebar:
        st.header("Filters")
        selected_sectors = set(st.multiselect("Sectors", all_sectors, default=[]))
        selected_tickers = set(st.multiselect("Tickers", all_tickers, default=[]))
        search = st.text_input("Keyword search", value="")

    compatibility = data["compatibility"]
    k1, k2, k3 = st.columns(3)
    k1.metric("Portfolio Stocks", len(holdings))
    k2.metric("Compatibility Score", f"{compatibility.score}/100")
    k3.metric("Macro Headlines", len(data["macro_rows"]))


    st.subheader("Portfolio Universe")
    st.dataframe(holdings, use_container_width=True, hide_index=True)

    st.subheader("Indian + Global + Geopolitical News")
    filtered_macro = _filter_rows(data["macro_rows"], sectors=selected_sectors, tickers=selected_tickers, query=search)
    st.dataframe(filtered_macro, use_container_width=True, hide_index=True)

    st.subheader("Sector News")
    filtered_sector = _filter_rows(data["sector_rows"], sectors=selected_sectors, tickers=set(), query=search)
    st.dataframe(filtered_sector, use_container_width=True, hide_index=True)

    st.subheader("Portfolio Stock News (Fundamental / Technical / Analyst)")
    filtered_portfolio = _filter_rows(data["portfolio_rows"], sectors=selected_sectors, tickers=selected_tickers, query=search)
    st.dataframe(filtered_portfolio, use_container_width=True, hide_index=True)

    st.subheader("Compatibility Interpretation")
    st.write(compatibility.interpretation)
    st.json(compatibility.details)

    st.subheader("AI Earnings Call Summary")
    st.dataframe(data["earnings_rows"], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
