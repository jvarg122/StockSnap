import sys
import time
from sqlalchemy.dialects.postgresql import insert

from app.alpha_vantage import AlphaVantageError, fetch_daily_series
from app.config import TICKER_INFO, WATCHLIST
from app.db import SessionLocal
from app.models import DailyPrice, Ticker

# alpha vantage rate limit fix
SECONDS_BETWEEN_REQUESTS = 13


def upsert_ticker(session, symbol: str, name: str, sector: str) -> None:
    stmt = insert(Ticker).values(symbol=symbol, name=name, sector=sector)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Ticker.symbol],
        set_={"name": stmt.excluded.name, "sector": stmt.excluded.sector},
    )
    session.execute(stmt)


def upsert_daily_prices(session, symbol: str, series: dict) -> int:
    if not series:
        return 0

    rows = [
        {"ticker_symbol": symbol, "date": date, "close": data["close"], "volume": data["volume"]}
        for date, data in series.items()
    ]
    stmt = insert(DailyPrice).values(rows)
    # duplicate error
    stmt = stmt.on_conflict_do_nothing(index_elements=["ticker_symbol", "date"])
    result = session.execute(stmt)
    return result.rowcount


def main() -> None:
    session = SessionLocal()
    total_new_rows = 0
    failures = []

    try:
        for i, symbol in enumerate(WATCHLIST):
            print(f"[{i + 1}/{len(WATCHLIST)}] fetching {symbol}...")

            try:
                series = fetch_daily_series(symbol)
            except AlphaVantageError as e:
                print(f"  FAILED: {e}", file=sys.stderr)
                failures.append(symbol)
                continue

            info = TICKER_INFO.get(symbol, {"name": symbol, "sector": "Unknown"})
            upsert_ticker(session, symbol, info["name"], info["sector"])
            new_rows = upsert_daily_prices(session, symbol, series)
            total_new_rows += new_rows
            print(f"  ok -- {new_rows} new rows")

            session.commit()

            if i < len(WATCHLIST) - 1:
                time.sleep(SECONDS_BETWEEN_REQUESTS)
    finally:
        session.close()

    print(f"\nDone. {total_new_rows} new daily_price rows across {len(WATCHLIST)} tickers.")
    if failures:
        print(f"Failed: {', '.join(failures)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
