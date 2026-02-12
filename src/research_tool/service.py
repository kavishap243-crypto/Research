from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from .ai_report import BasicAIEarningsSummarizer
from .models import EarningsCallReport, NewsCategory, NewsItem, PortfolioStock
from .providers import GoogleNewsRSSProvider, TranscriptLinkProvider, sorted_unique


@dataclass(slots=True)
class CompatibilityResult:
    score: float
    details: dict[str, float]
    interpretation: str


class ResearchFilterService:
    def __init__(
        self,
        news_provider: GoogleNewsRSSProvider | None = None,
        transcript_provider: TranscriptLinkProvider | None = None,
        earnings_summarizer: BasicAIEarningsSummarizer | None = None,
    ) -> None:
        self.news_provider = news_provider or GoogleNewsRSSProvider()
        self.transcript_provider = transcript_provider or TranscriptLinkProvider()
        self.earnings_summarizer = earnings_summarizer or BasicAIEarningsSummarizer()

    def fetch_macro_news(self) -> list[NewsItem]:
        queries = {
            "Indian stock market news": {NewsCategory.INDIAN},
            "global market outlook": {NewsCategory.GLOBAL},
            "geopolitical impact on markets": {NewsCategory.GEOPOLITICAL},
        }
        collected: list[NewsItem] = []
        for query, categories in queries.items():
            collected.extend(self.news_provider.fetch(query, categories))
        return sorted_unique(collected)

    def fetch_sector_news(self, sectors: Iterable[str]) -> dict[str, list[NewsItem]]:
        by_sector: dict[str, list[NewsItem]] = {}
        for sector in sectors:
            query = f"{sector} sector India listed companies"
            items = self.news_provider.fetch(query, {NewsCategory.SECTOR}, sector=sector)
            by_sector[sector] = sorted_unique(items)
        return by_sector

    def fetch_portfolio_news(self, portfolio: Iterable[PortfolioStock]) -> dict[str, list[NewsItem]]:
        out: dict[str, list[NewsItem]] = {}
        tags = {
            "fundamental": NewsCategory.FUNDAMENTAL,
            "technical": NewsCategory.TECHNICAL,
            "analyst call": NewsCategory.ANALYST,
        }
        for stock in portfolio:
            collected: list[NewsItem] = []
            for suffix, category in tags.items():
                query = f"{stock.company_name} {stock.ticker} {suffix}"
                collected.extend(self.news_provider.fetch(query, {category}, ticker=stock.ticker, sector=stock.sector))
            out[stock.ticker] = sorted_unique(collected)
        return out

    def compute_sector_compatibility(
        self,
        portfolio: Iterable[PortfolioStock],
        sector_news: dict[str, list[NewsItem]],
    ) -> CompatibilityResult:
        sector_scores = defaultdict(float)
        sector_weights = defaultdict(float)

        for stock in portfolio:
            sentiment = self._estimate_sector_sentiment(sector_news.get(stock.sector, []))
            sector_scores[stock.sector] += sentiment * stock.weight
            sector_weights[stock.sector] += stock.weight

        detail_scores = {
            sector: round(sector_scores[sector] / sector_weights[sector], 3)
            for sector in sector_scores
            if sector_weights[sector] > 0
        }

        if not detail_scores:
            return CompatibilityResult(0.0, {}, "insufficient data")

        weighted_total = sum(detail_scores.values()) / len(detail_scores)
        score = round((weighted_total + 1) * 50, 2)  # normalize [-1,1] to [0,100]

        if score >= 70:
            interpretation = "highly compatible with current sector tone"
        elif score >= 45:
            interpretation = "moderately compatible; selective risk management advised"
        else:
            interpretation = "low compatibility; review concentration and hedging"

        return CompatibilityResult(score=score, details=detail_scores, interpretation=interpretation)

    def generate_earnings_reports(
        self,
        portfolio: Iterable[PortfolioStock],
        transcript_snippets: dict[str, list[str]],
        quarter: str,
    ) -> list[EarningsCallReport]:
        reports: list[EarningsCallReport] = []
        for stock in portfolio:
            summary, points = self.earnings_summarizer.summarize(transcript_snippets.get(stock.ticker, []))
            reports.append(
                EarningsCallReport(
                    ticker=stock.ticker,
                    company_name=stock.company_name,
                    quarter=quarter,
                    ai_summary=summary,
                    key_takeaways=points,
                    transcript_links=self.transcript_provider.for_stock(stock),
                )
            )
        return reports

    @staticmethod
    def _estimate_sector_sentiment(news_items: list[NewsItem]) -> float:
        if not news_items:
            return 0.0
        positive_terms = ("beat", "growth", "upgrade", "expansion", "strong", "rally")
        negative_terms = ("miss", "downgrade", "decline", "weak", "fall", "risk")

        score = 0
        for item in news_items:
            text = f"{item.title} {item.summary}".lower()
            score += sum(1 for t in positive_terms if t in text)
            score -= sum(1 for t in negative_terms if t in text)

        scaled = max(-1.0, min(1.0, score / max(3, len(news_items))))
        return scaled
