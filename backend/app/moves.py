import datetime

TOP_N = 5
WINDOW_DAYS = 20  # how far back to look for the volume average
MIN_DAYS = 5  # need at least this many days sample size
SPIKE_THRESHOLD = 2.0
RELATIVE_PERF_THRESHOLD = 3.0 

def pct_change(prev_close, close):
    return (close - prev_close) / prev_close * 100

def volume_ratio(volume, avg_volume):
    if avg_volume == 0:
        return 0.0
    return volume /avg_volume


def compute_ticker_metrics(history: list[dict], target_date: datetime.date) -> dict | None:
    # history sorted oldest to newest, each row just a dict with date/close/volume
    dates = [row["date"] for row in history]
    if target_date not in dates:
        return None

    idx = dates.index(target_date)
    metrics = {"pct_change": None, "volume_ratio": None}

    if idx > 0:
        metrics["pct_change"] = pct_change(history[idx - 1]["close"], history[idx]["close"])

    trailing = history[max(0, idx - WINDOW_DAYS):idx]
    if len(trailing) >= MIN_DAYS:
        avg_volume = sum(row["volume"] for row in trailing) / len(trailing)
        metrics["volume_ratio"] = volume_ratio(history[idx]["volume"], avg_volume)

    return metrics

def rank_top_movers(pct_changes, top_n=TOP_N):
    # split by positive and negative sign first otherwise a small list could tag the same stock as both a top gainer and a top loser
    gains = {}
    losses = {}
    for symbol, value in pct_changes.items():
        if value > 0:
            gains[symbol] = value
        elif value < 0:
            losses[symbol] = value

    gainers = sorted(gains.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    losers = sorted(losses.items(), key=lambda kv: kv[1])[:top_n]
    return gainers, losers

def find_volume_spikes(volume_ratios, threshold=SPIKE_THRESHOLD):
    spikes = [(symbol, ratio) for symbol, ratio in volume_ratios.items() if ratio >= threshold]
    spikes.sort(key=lambda kv: kv[1], reverse=True)
    return spikes


def find_relative_performance(pct_changes, sectors, threshold=RELATIVE_PERF_THRESHOLD):
    sector_changes = {} #group by sector
    for symbol, change in pct_changes.items():
        sector = sectors.get(symbol)
        if sector is None:
            continue
        sector_changes.setdefault(sector, []).append(change)

    sector_avg = {sector: sum(values) / len(values) for sector, values in sector_changes.items()} #stock's own % change - sector average % change
    
    # compare each stock to its sector
    relative_performance = []
    for symbol, change in pct_changes.items():
        sector = sectors.get(symbol)
        if sector is None:
            continue
        deviation = change - sector_avg[sector]
        if abs(deviation) >= threshold:
            relative_performance.append((symbol, round(deviation, 2)))

    relative_performance.sort(key=lambda kv: abs(kv[1]), reverse=True)
    return relative_performance
