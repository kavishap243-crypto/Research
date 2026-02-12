from __future__ import annotations

from dataclasses import asdict

from .models import EarningsCallReport, NewsItem, PortfolioStock


def flatten_news(items: list[NewsItem]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in items:
        rows.append(
            {
                "published_at": item.published_at.strftime("%Y-%m-%d %H:%M"),
                "title": item.title,
                "source": item.source,
                "url": item.source_url,
                "ticker": item.ticker or "",
                "sector": item.sector or "",
                "categories": ", ".join(sorted(c.value for c in item.categories)),
            }
        )
    return rows


def flatten_sector_news(sector_news: dict[str, list[NewsItem]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for sector, items in sector_news.items():
        for item in items:
            rows.append(
                {
                    "sector": sector,
                    "published_at": item.published_at.strftime("%Y-%m-%d %H:%M"),
                    "title": item.title,
                    "source": item.source,
                    "url": item.source_url,
                }
            )
    return rows


def flatten_portfolio_news(portfolio_news: dict[str, list[NewsItem]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ticker, items in portfolio_news.items():
        for item in items:
            rows.append(
                {
                    "ticker": ticker,
                    "published_at": item.published_at.strftime("%Y-%m-%d %H:%M"),
                    "title": item.title,
                    "source": item.source,
                    "url": item.source_url,
                    "sector": item.sector or "",
                    "categories": ", ".join(sorted(c.value for c in item.categories)),
                }
            )
    return rows


def portfolio_rows(portfolio: list[PortfolioStock]) -> list[dict[str, str | float]]:
    return [
        {
            "company": s.company_name,
            "ticker": s.ticker,
            "sector": s.sector,
            "weight": s.weight,
        }
        for s in portfolio
    ]


def earnings_rows(reports: list[EarningsCallReport]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for report in reports:
        row = asdict(report)
        row["key_takeaways"] = " | ".join(report.key_takeaways)
        row["nse_link"] = report.transcript_links.get("NSE", "")
        row["bse_link"] = report.transcript_links.get("BSE", "")
        rows.append(row)
    return rows

