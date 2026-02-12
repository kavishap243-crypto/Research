# Research & Filter Tool for Stocks

This project supports a **true interactive live dashboard** for stock research, and a separate static HTML export.

## See the dashboard now (live)

```bash
pip install -e .
streamlit run src/research_tool/dashboard.py
```

Open the URL shown by Streamlit (typically `http://localhost:8501`).

### Refresh behavior

- Auto-refresh every 300 seconds (5 minutes).
- Manual **Refresh now** button is available.

## Convert code output into an HTML file

If you want a downloadable/shareable HTML file from this codebase, run:

```bash
python -m src.research_tool.main
```

This generates:

- `portfolio_research_report.html`

You can open it directly in any browser.

## Run tests

```bash
pytest -q
```

## Included sample portfolio

The demo includes your requested companies/tickers (28 holdings): BBTC, RELIANCE, LEMONTREE, LODHA, BRIGADE, ARE&M, 532174, EIHOTEL, 543232, IEX, INDIGOPNTS, JKIL, AFCONS, PNBHOUSING, M&M, MAHABANK, SHRIRAMFIN, 544172, SBILIFE, LUPIN, WAAREEENER, 544008, MAHSCOOTER, ABBOTINDIA, ASKAUTOLTD, MSUMI, MARUTI, POLYCAB.

## Notes

- News ingestion may return empty lists in restricted environments (network/proxy constraints).
- The default AI summarizer is deterministic and offline-friendly.
