from app.models import DailyPrice

TREND_WINDOW_DAYS = 10  # how far to look back

def get_price_trend(session, symbol: str, target_date) -> dict | None:
    """Summarizes a ticker's price direction over the trailing N days, ending on
    target_date. Lets the "why did it move" explanation distinguish a sudden
    spike from the continuation of a trend that was already building."""
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