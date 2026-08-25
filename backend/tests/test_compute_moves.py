import datetime

from scripts.compute_moves import (
    label,
    lastprice_date,
    price_hist,
    replaceMoves_date,
    upsert_snapshot,
)
from scripts.fetch_prices import upsert_daily_prices, upsert_ticker
from app.models import Move, Snapshot

def seed_prices(session, symbol, rows):
    upsert_ticker(session, symbol, symbol, "Technology")
    series = {}
    for i, (close, volume) in enumerate(rows):
        series[datetime.date(2026, 1, i + 1)] = {"close": close, "volume": volume}
    upsert_daily_prices(session, symbol, series)
    session.commit()

def test_lastprice_date(db_session):
    seed_prices(db_session, "AAPL", [(100, 1000), (105, 1000)])
    assert lastprice_date(db_session) == datetime.date(2026, 1, 2)

# if the table is empty
def emptyTable(db_session):
    assert lastprice_date(db_session) is None

def priceHist_test(db_session):
    seed_prices(db_session, "AAPL", [(100, 1000), (105, 1000), (110, 1000)])
    history = price_hist(db_session, "AAPL")
    result_dates = [row["date"] for row in history]
    assert result_dates == [datetime.date(2026, 1, 1), datetime.date(2026, 1, 2), datetime.date(2026, 1, 3)]

def test_duplicate(db_session):
    seed_prices(db_session, "AAPL", [(100, 1000)])
    target_date = datetime.date(2026, 1, 1)
    upsert_snapshot(db_session, target_date)
    db_session.commit()

    first_move = {"snapshot_date": target_date, "ticker_symbol": "AAPL", "move_type": "top_gainer", "value": 5.0}
    replaceMoves_date(db_session, target_date, [first_move])
    db_session.commit()
    assert db_session.query(Move).filter_by(snapshot_date=target_date).count() == 1

    # if diff move for same date overwrite it
    second_move = {"snapshot_date": target_date, "ticker_symbol": "AAPL", "move_type": "top_loser", "value": -5.0}
    replaceMoves_date(db_session, target_date, [second_move])
    db_session.commit()
    moves = db_session.query(Move).filter_by(snapshot_date=target_date).all()
    assert len(moves) == 1
    assert moves[0].move_type == "top_loser"

# check so that each of tickers gets labeled with 3 move
def tests_labels():
    target_date = datetime.date(2026, 1, 1)
    pct_changes = {"AAPL": 10.0, "TSLA": -8.0}
    volume_ratios = {"NVDA": 3.0}

    rows = label(target_date, pct_changes, volume_ratios)
    by_symbol = {row["ticker_symbol"]: row["move_type"] for row in rows}
    assert by_symbol["AAPL"] == "top_gainer"
    assert by_symbol["TSLA"] == "top_loser"
    assert by_symbol["NVDA"] == "volume_spike"
