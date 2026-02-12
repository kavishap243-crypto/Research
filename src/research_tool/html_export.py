from __future__ import annotations

from datetime import datetime, timezone
from html import escape

from .models import EarningsCallReport, NewsItem, PortfolioStock
from .service import CompatibilityResult


def _news_list(items: list[NewsItem], limit: int = 8) -> str:
    rows: list[str] = []
    for item in items[:limit]:
        date = item.published_at.strftime("%Y-%m-%d %H:%M")
        rows.append(
            "<li>"
            f"<a href='{escape(item.source_url)}' target='_blank' rel='noreferrer'>{escape(item.title)}</a>"
            f" <small>({escape(item.source)} • {date})</small>"
            "</li>"
        )
    if not rows:
        return "<p>No news found.</p>"
    return f"<ul>{''.join(rows)}</ul>"


def build_html_report(
    *,
    portfolio: list[PortfolioStock],
    macro_news: list[NewsItem],
    sector_news: dict[str, list[NewsItem]],
    portfolio_news: dict[str, list[NewsItem]],
    compatibility: CompatibilityResult,
    earnings_reports: list[EarningsCallReport],
) -> str:
    created = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    portfolio_rows = "".join(
        f"<tr><td>{escape(stock.company_name)}</td><td>{escape(stock.ticker)}</td><td>{escape(stock.sector)}</td><td>{stock.weight:.3f}</td></tr>"
        for stock in portfolio
    )

    sector_blocks = "".join(
        f"<h3>{escape(sector)}</h3>{_news_list(items)}"
        for sector, items in sector_news.items()
    )

    portfolio_blocks = "".join(
        f"<h3>{escape(ticker)}</h3>{_news_list(items, limit=6)}"
        for ticker, items in portfolio_news.items()
    )

    earnings_blocks = "".join(
        "<article class='card'>"
        f"<h3>{escape(report.company_name)} ({escape(report.ticker)})</h3>"
        f"<p><strong>{escape(report.quarter)}:</strong> {escape(report.ai_summary)}</p>"
        f"<ul>{''.join(f'<li>{escape(point)}</li>' for point in report.key_takeaways)}</ul>"
        f"<p>Transcript links: <a href='{escape(report.transcript_links.get('NSE', '#'))}' target='_blank'>NSE</a> | "
        f"<a href='{escape(report.transcript_links.get('BSE', '#'))}' target='_blank'>BSE</a></p>"
        "</article>"
        for report in earnings_reports
    )

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Portfolio Research Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.45; }}
h1, h2 {{ margin-bottom: 8px; }}
section {{ margin-bottom: 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f6f6f6; }}
.card {{ border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 12px; }}
.note {{ color: #555; font-size: 0.9em; }}
</style>
</head>
<body>
<h1>Stock Research & Filter Report</h1>
<p class='note'>Generated: {created}</p>
<p class='note'>This file is downloadable as <code>portfolio_research_report.html</code>.</p>

<section>
  <h2>Portfolio Universe ({len(portfolio)} stocks)</h2>
  <table>
    <thead><tr><th>Company</th><th>Ticker</th><th>Sector</th><th>Weight</th></tr></thead>
    <tbody>{portfolio_rows}</tbody>
  </table>
</section>

<section>
  <h2>Indian, Global & Geopolitical News</h2>
  {_news_list(macro_news, limit=20)}
</section>

<section>
  <h2>Sector News</h2>
  {sector_blocks}
</section>

<section>
  <h2>Portfolio Stock News (Fundamental/Technical/Analyst)</h2>
  {portfolio_blocks}
</section>

<section>
  <h2>Sector Compatibility Test</h2>
  <p><strong>Score:</strong> {compatibility.score}/100</p>
  <p><strong>Interpretation:</strong> {escape(compatibility.interpretation)}</p>
  <pre>{escape(str(compatibility.details))}</pre>
</section>

<section>
  <h2>AI Earnings Call Report</h2>
  {earnings_blocks}
</section>
</body>
</html>
"""
