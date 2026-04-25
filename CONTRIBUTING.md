# Contributing

## Setup
```bash
git clone https://github.com/VasundharaShivankar/stock-market-dashboard.git
cd stock-market-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Adding a New Indicator
1. Add calculation in `src/indicators.py`
2. Add chart trace in `src/charts.py`
3. Add checkbox in `app.py` sidebar
4. Add to `config.py` if it needs constants

## Adding a New Data Source
1. Add fetcher function in `src/data_fetcher.py`
2. Export it from `src/__init__.py`
3. Use it in `app.py`

## Commit Convention
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code cleanup
- `docs:` documentation only