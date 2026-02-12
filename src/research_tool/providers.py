from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import quote_plus
from urllib.error import URLError
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from .models import NewsCategory, NewsItem, PortfolioStock


@dataclass(slots=True)
class GoogleNewsRSSProvider:
    """Simple RSS provider using Google News search as an index of publisher links."""

    max_items: int = 12

    def fetch(self, query: str, categories: set[NewsCategory], *, sector: str | None = None, ticker: str | None = None) -> list[NewsItem]:
        encoded = quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            with urlopen(url, timeout=10) as response:
                data = response.read()
            root = ET.fromstring(data)
        except (URLError, TimeoutError, ET.ParseError):
            return []

        items = []
        for item in root.findall("./channel/item")[: self.max_items]:
            title = item.findtext("title", default="Untitled")
            link = item.findtext("link", default="")
            pub_date = item.findtext("pubDate", default="")
            source_el = item.find("source")
            source_name = source_el.text if source_el is not None else "Unknown"

            try:
                published_at = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
            except ValueError:
                published_at = datetime.now(timezone.utc)

            items.append(
                NewsItem(
                    title=title,
                    summary=f"Query match for '{query}'",
                    source=source_name,
                    source_url=link,
                    published_at=published_at,
                    categories=categories,
                    sector=sector,
                    ticker=ticker,
                )
            )
        return items


@dataclass(slots=True)
class TranscriptLinkProvider:
    """Builds third-party transcript links for NSE and BSE."""

    def for_stock(self, stock: PortfolioStock) -> dict[str, str]:
        ticker = stock.ticker.upper()
        encoded_ticker = quote_plus(ticker)
        return {
            "NSE": f"https://www.nseindia.com/get-quotes/equity?symbol={encoded_ticker}",
            "BSE": f"https://www.bseindia.com/stock-share-price/{encoded_ticker}",
        }


def sorted_unique(items: Iterable[NewsItem]) -> list[NewsItem]:
    seen: set[tuple[str, str]] = set()
    out: list[NewsItem] = []
    for item in items:
        key = (item.title, item.source_url)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    out.sort(key=lambda i: i.published_at, reverse=True)
    return out
