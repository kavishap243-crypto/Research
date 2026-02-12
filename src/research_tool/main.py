from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .html_export import build_html_report
from .models import PortfolioStock
from .service import ResearchFilterService


def sample_portfolio() -> list[PortfolioStock]:
    return [
        PortfolioStock(ticker="BBTC", company_name="THE BOMBAY BURMAH TRADING CORPORATION LIMITED", sector="Conglomerate", weight=0.035),
        PortfolioStock(ticker="RELIANCE", company_name="RELIANCE INDUSTRIES LIMITED", sector="Energy", weight=0.04),
        PortfolioStock(ticker="LEMONTREE", company_name="LEMON TREE HOTELS LIMITED", sector="Hospitality", weight=0.035),
        PortfolioStock(ticker="LODHA", company_name="LODHA DEVELOPERS LIMITED", sector="Real Estate", weight=0.035),
        PortfolioStock(ticker="BRIGADE", company_name="BRIGADE ENTERPRISES LIMITED", sector="Real Estate", weight=0.035),
        PortfolioStock(ticker="ARE&M", company_name="AMARA RAJA ENERGY & MOBILITY LIMITED", sector="Energy Storage", weight=0.035),
        PortfolioStock(ticker="532174", company_name="ICICI BANK LIMITED", sector="Banking", weight=0.04),
        PortfolioStock(ticker="EIHOTEL", company_name="EIH LIMITED", sector="Hospitality", weight=0.035),
        PortfolioStock(ticker="543232", company_name="COMPUTER AGE MANAGEMENT SERVICES LIMITED", sector="Financial Services", weight=0.035),
        PortfolioStock(ticker="IEX", company_name="INDIAN ENERGY EXCHANGE LIMITED", sector="Power Exchange", weight=0.035),
        PortfolioStock(ticker="INDIGOPNTS", company_name="Indigo Paints Ltd", sector="Chemicals", weight=0.035),
        PortfolioStock(ticker="JKIL", company_name="J. KUMAR INFRAPROJECTS LIMITED", sector="Infrastructure", weight=0.035),
        PortfolioStock(ticker="AFCONS", company_name="AFCONS INFRASTRUCTURE LIMITED", sector="Infrastructure", weight=0.035),
        PortfolioStock(ticker="PNBHOUSING", company_name="PNB HOUSING FINANCE LIMITED", sector="Housing Finance", weight=0.035),
        PortfolioStock(ticker="M&M", company_name="MAHINDRA AND MAHINDRA LIMITED", sector="Automobile", weight=0.04),
        PortfolioStock(ticker="MAHABANK", company_name="THE BANK OF MAHARASHTRA LIMITED", sector="Banking", weight=0.035),
        PortfolioStock(ticker="SHRIRAMFIN", company_name="SHRIRAM FINANCE LIMITED", sector="Financial Services", weight=0.035),
        PortfolioStock(ticker="544172", company_name="INDEGENE LIMITED", sector="Healthcare Services", weight=0.035),
        PortfolioStock(ticker="SBILIFE", company_name="SBI LIFE INSURANCE COMPANY LIMITED", sector="Insurance", weight=0.035),
        PortfolioStock(ticker="LUPIN", company_name="LUPIN LIMITED", sector="Pharmaceuticals", weight=0.035),
        PortfolioStock(ticker="WAAREEENER", company_name="WAAREE ENERGIES LIMITED", sector="Renewables", weight=0.035),
        PortfolioStock(ticker="544008", company_name="MAX ESTATES LIMITED", sector="Real Estate", weight=0.035),
        PortfolioStock(ticker="MAHSCOOTER", company_name="MAHARASHTRA SCOOTERS LTD", sector="Automobile", weight=0.03),
        PortfolioStock(ticker="ABBOTINDIA", company_name="ABBOTT INDIA LIMITED", sector="Pharmaceuticals", weight=0.035),
        PortfolioStock(ticker="ASKAUTOLTD", company_name="ASK AUTOMOTIVE LIMITED", sector="Automobile", weight=0.035),
        PortfolioStock(ticker="MSUMI", company_name="MOTHERSON SUMI WIRING INDIA LIMITED", sector="Auto Components", weight=0.035),
        PortfolioStock(ticker="MARUTI", company_name="MARUTI SUZUKI INDIA LIMITED", sector="Automobile", weight=0.04),
        PortfolioStock(ticker="POLYCAB", company_name="POLYCAB INDIA LIMITED", sector="Electrical Equipment", weight=0.04),
    ]


def demo(output_html: str = "portfolio_research_report.html") -> dict:
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

    result = {
        "macro_news_count": len(macro_news),
        "sector_news_count": {k: len(v) for k, v in sector_news.items()},
        "portfolio_news_count": {k: len(v) for k, v in portfolio_news.items()},
        "compatibility": asdict(compatibility),
        "earnings_reports": [asdict(r) for r in earnings_reports],
    }

    html = build_html_report(
        portfolio=portfolio,
        macro_news=macro_news,
        sector_news=sector_news,
        portfolio_news=portfolio_news,
        compatibility=compatibility,
        earnings_reports=earnings_reports,
    )
    Path(output_html).write_text(html, encoding="utf-8")
    result["html_report_file"] = output_html
    return result


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
