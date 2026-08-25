import datetime

from app.moves import (
    compute_ticker_metrics,
    find_volume_spikes,
    pct_change,
    rank_top_movers,
    volume_ratio,
)

def test_pct_change_positive():
    assert pct_change(100, 110) == 10.0

def test_pct_change_negative():
    assert pct_change(100, 90) == -10.0


def test_volume_ratio():
    assert volume_ratio(200, 100) == 2.0


def _history(rows):
    return [{"date": d, "close": c, "volume": v} for d, c, v in rows]

def test_pct_change():
    history = _history([
        (datetime.date(2026, 1, 1), 100, 1000),
        (datetime.date(2026, 1, 2), 110, 1000),
    ])
    metrics = compute_ticker_metrics(history, datetime.date(2026, 1, 2))
    assert metrics["pct_change"] == 10.0

#has enough history
def test_volume_ratio_history():
    dates = [datetime.date(2026, 1, i) for i in range(1, 7)]
    rows = [(d, 100, 1000) for d in dates[:5]] + [(dates[5], 100, 5000)]
    history = _history(rows)
    metrics = compute_ticker_metrics(history, dates[5])
    assert metrics["volume_ratio"] == 5.0


# check gainers/losers get sorted right and top_n limits the list
def test_rank_top_movers():
    pct_changes = {"A": 5.0, "B": -3.0, "C": 10.0, "D": -8.0, "E": 1.0}
    gainers, losers = rank_top_movers(pct_changes, top_n=2)
    assert gainers == [("C", 10.0), ("A", 5.0)]
    assert losers == [("D", -8.0), ("B", -3.0)]

# over threshold
def test_find_volume_spikes():
    ratios = {"A": 1.5, "B": 3.0, "C": 2.0, "D": 0.5}
    spikes = find_volume_spikes(ratios, threshold=2.0)
    assert spikes == [("B", 3.0), ("C", 2.0)]
