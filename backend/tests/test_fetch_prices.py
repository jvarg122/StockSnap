import datetime
from scripts.fetch_prices import upsert_daily_prices, upsert_ticker
from app.models import DailyPrice, Ticker


def test_new_ticker(db_session):
    upsert_ticker(db_session, "AAPL", "Apple", "Technology")
    db_session.commit()

    ticker = db_session.get(Ticker, "AAPL")
    assert ticker.name == "Apple"
    assert ticker.sector == "Technology"


def test_ticker_update(db_session):
    upsert_ticker(db_session, "AAPL", "name", "sector")
    db_session.commit()

    # same symbol again, different name and 11 GICS sector 
    # update existing row
    upsert_ticker(db_session, "AAPL", "Apple", "Technology")
    db_session.commit()

    tickers = db_session.query(Ticker).filter_by(symbol="AAPL").all()
    assert len(tickers) == 1
    assert tickers[0].name == "Apple"


def test_insert_prices(db_session):
    upsert_ticker(db_session, "AAPL", "Apple", "Technology")
    db_session.commit()

    series = {
        datetime.date(2026, 8, 14): {"close": 230.5, "volume": 42_000_000},
        datetime.date(2026, 8, 13): {"close": 228.1, "volume": 39_000_000},
    }
    new_rows = upsert_daily_prices(db_session, "AAPL", series)
    db_session.commit()

    assert new_rows == 2
    prices = db_session.query(DailyPrice).filter_by(ticker_symbol="AAPL").all()
    assert len(prices) == 2
