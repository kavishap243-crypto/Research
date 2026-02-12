from __future__ import annotations

from datetime import datetime, timezone

from research_tool.dashboard_data import flatten_news, flatten_portfolio_news, flatten_sector_news
from research_tool.models import NewsCategory, NewsItem


def _sample_item(title: str, *, ticker: str | None = None, sector: str | None = None):
    return NewsItem(
        title=title,
        summary="summary",
        source="Reuters",
        source_url="https://example.com/news",
        published_at=datetime.now(timezone.utc),
        categories={NewsCategory.INDIAN},
        ticker=ticker,
        sector=sector,
    )


def test_flatten_news_maps_expected_fields():
    rows = flatten_news([_sample_item("Headline", ticker="TCS", sector="IT")])
    assert rows[0]["title"] == "Headline"
    assert rows[0]["ticker"] == "TCS"
    assert rows[0]["sector"] == "IT"


def test_flatten_sector_news_contains_sector_column():
    rows = flatten_sector_news({"Banking": [_sample_item("Bank update", sector="Banking")]})
    assert rows[0]["sector"] == "Banking"


def test_flatten_portfolio_news_contains_ticker_column():
    rows = flatten_portfolio_news({"RELIANCE": [_sample_item("Energy update", ticker="RELIANCE", sector="Energy")]})
    assert rows[0]["ticker"] == "RELIANCE"

