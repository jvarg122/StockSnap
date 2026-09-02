from app.models import DailyPrice, Move, Ticker

TREND_WINDOW_DAYS = 10  # how far to look back

def get_price_trend(session, symbol: str, target_date) -> dict | None:
    rows = (
        session.query(DailyPrice.date, DailyPrice.close)
        .filter(
            DailyPrice.ticker_symbol == symbol, 
            DailyPrice.date <= target_date
        )
        .order_by(DailyPrice.date.desc())
        .limit(TREND_WINDOW_DAYS)
        .all()
    )

    if len(rows) < 2:
        return None

    rows.reverse()

    closes = []

    for row in rows:
        closes.append(float(row.close))

# count up and down days
    upDays = 0
    downDays = 0

    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            upDays += 1
        elif closes[i] < closes[i - 1]:
            downDays += 1

    #calculate the % change
    start_close = closes[0]
    end_close = closes[-1]

    pctChange = ( # % change over window
        (end_close - start_close) / start_close * 100
    )

    return {
        "days": len(closes),
        "start_close": start_close,
        "end_close": end_close,
        "pctChange": round(pctChange, 2),
        "upDays": upDays,
        "downDays": downDays,
    }

def get_sector_context(session, symbol: str, target_date) -> dict | None:
    ticker = session.get(Ticker, symbol)
    if ticker is None:
        return None

    other_moves = (
        session.query(Move, Ticker)
        .join(Ticker, Move.ticker_symbol == Ticker.symbol)
        .filter(
            Move.snapshot_date == target_date,
            Ticker.sector == ticker.sector,
            Move.ticker_symbol != symbol,
        )
        .all()
    )

    otherMovers = [] #

    for move, _ in other_moves:
        mover = {
            "symbol": move.ticker_symbol,
            "moveType": move.move_type,
            "value": float(move.value)
        }

        otherMovers.append(mover)

    return {
        "sector": ticker.sector,
        "otherMoversCount": len(other_moves),
        "otherMovers": otherMovers,
    }