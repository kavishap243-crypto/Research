from __future__ import annotations

from datetime import datetime, timezone

from research_tool.ai_report import BasicAIEarningsSummarizer
from research_tool.html_export import build_html_report
from research_tool.main import sample_portfolio
from research_tool.models import NewsCategory, NewsItem, PortfolioStock
from research_tool.providers import TranscriptLinkProvider
from research_tool.service import CompatibilityResult, ResearchFilterService


class FakeNewsProvider:
    def fetch(self, query, categories, sector=None, ticker=None):
        base = NewsItem(
            title=f"{query} shows strong growth outlook",
            summary="Analyst upgrade after earnings beat.",
            source="Reuters",
            source_url=f"https://example.com/{query.replace(' ', '-')}",
            published_at=datetime.now(timezone.utc),
            categories=categories,
            sector=sector,
            ticker=ticker,
        )
        return [base]


def test_fetch_portfolio_news_has_all_tickers():
    svc = ResearchFilterService(news_provider=FakeNewsProvider())
    portfolio = [
        PortfolioStock(ticker="TCS", company_name="TCS", sector="IT"),
        PortfolioStock(ticker="INFY", company_name="Infosys", sector="IT"),
    ]

    result = svc.fetch_portfolio_news(portfolio)

    assert set(result.keys()) == {"TCS", "INFY"}
    assert all(len(items) == 3 for items in result.values())


def test_compatibility_score_is_normalized():
    svc = ResearchFilterService(news_provider=FakeNewsProvider())
    portfolio = [PortfolioStock(ticker="TCS", company_name="TCS", sector="IT", weight=1.0)]
    sector_news = {
        "IT": [
            NewsItem(
                title="IT sector earnings beat and rally continues",
                summary="Strong expansion and upgrade cycle",
                source="Mint",
                source_url="https://example.com/news1",
                published_at=datetime.now(timezone.utc),
                categories={NewsCategory.SECTOR},
                sector="IT",
            )
        ]
    }

    result = svc.compute_sector_compatibility(portfolio, sector_news)

    assert 0 <= result.score <= 100
    assert result.score > 50


def test_earnings_report_has_transcript_links_and_takeaways():
    svc = ResearchFilterService(
        news_provider=FakeNewsProvider(),
        transcript_provider=TranscriptLinkProvider(),
        earnings_summarizer=BasicAIEarningsSummarizer(),
    )
    portfolio = [PortfolioStock(ticker="TCS", company_name="TCS", sector="IT")]
    reports = svc.generate_earnings_reports(
        portfolio,
        transcript_snippets={
            "TCS": [
                "Management highlighted strong demand and margin improvement.",
                "Analysts questioned attrition and pricing discipline.",
            ]
        },
        quarter="Q3 FY26",
    )

    assert len(reports) == 1
    assert "NSE" in reports[0].transcript_links
    assert "BSE" in reports[0].transcript_links
    assert reports[0].key_takeaways


def test_sample_portfolio_includes_requested_holdings_count():
    holdings = sample_portfolio()
    assert len(holdings) == 28
    tickers = {h.ticker for h in holdings}
    assert {"BBTC", "RELIANCE", "ARE&M", "M&M", "POLYCAB"}.issubset(tickers)


def test_transcript_provider_url_encodes_special_tickers():
    provider = TranscriptLinkProvider()
    links = provider.for_stock(PortfolioStock(ticker="M&M", company_name="Mahindra and Mahindra", sector="Auto"))
    assert "M%26M" in links["NSE"]


def test_html_report_contains_company_and_links():
    portfolio = [PortfolioStock(ticker="BBTC", company_name="THE BOMBAY BURMAH TRADING CORPORATION LIMITED", sector="Conglomerate")]
    macro_news = [
        NewsItem(
            title="India market opens firm",
            summary="Broad based gains.",
            source="Bloomberg",
            source_url="https://example.com/macro",
            published_at=datetime.now(timezone.utc),
            categories={NewsCategory.INDIAN},
        )
    ]
    sector_news = {"Conglomerate": macro_news}
    portfolio_news = {"BBTC": macro_news}
    compatibility = CompatibilityResult(score=66.0, details={"Conglomerate": 0.32}, interpretation="moderately compatible")
    report = build_html_report(
        portfolio=portfolio,
        macro_news=macro_news,
        sector_news=sector_news,
        portfolio_news=portfolio_news,
        compatibility=compatibility,
        earnings_reports=[],
    )

    assert "THE BOMBAY BURMAH TRADING CORPORATION LIMITED" in report
    assert "https://example.com/macro" in report
    assert "Sector Compatibility Test" in report
