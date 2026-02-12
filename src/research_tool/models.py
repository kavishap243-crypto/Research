from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NewsCategory(str, Enum):
    INDIAN = "indian"
    GLOBAL = "global"
    GEOPOLITICAL = "geopolitical"
    SECTOR = "sector"
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    ANALYST = "analyst"
    EARNINGS = "earnings"


@dataclass(slots=True)
class NewsItem:
    title: str
    summary: str
    source: str
    source_url: str
    published_at: datetime
    categories: set[NewsCategory]
    ticker: str | None = None
    sector: str | None = None


@dataclass(slots=True)
class PortfolioStock:
    ticker: str
    company_name: str
    sector: str
    weight: float = 1.0


@dataclass(slots=True)
class EarningsCallReport:
    ticker: str
    company_name: str
    quarter: str
    ai_summary: str
    key_takeaways: list[str] = field(default_factory=list)
    transcript_links: dict[str, str] = field(default_factory=dict)
