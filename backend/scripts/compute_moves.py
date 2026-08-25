import datetime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from app.config import WATCHLIST
from app.db import SessionLocal
from app.models import DailyPrice, Move, Snapshot
from app.moves import compute_ticker_metrics, find_volume_spikes, rank_top_movers

def lastprice_date(session) -> datetime.date | None:
    #whatever day fetch_prices last grabbed is today
    return session.query(func.max(DailyPrice.date)).scalar()


def price_hist(session, symbol: str) -> list[dict]:
    rows = (
        session.query(DailyPrice)
        .filter(DailyPrice.ticker_symbol == symbol)
        .order_by(DailyPrice.date)
        .all()
    )
    return [{"date": row.date, "close": float(row.close), "volume": row.volume} for row in rows]

def upsert_snapshot(session, target_date: datetime.date) -> None:
    stmt = insert(Snapshot).values(date=target_date, computed_at=datetime.datetime.now(datetime.UTC))
    stmt = stmt.on_conflict_do_update(
        index_elements=[Snapshot.date],
        set_={"computed_at": stmt.excluded.computed_at},
    )
    session.execute(stmt)

def replaceMoves_date(session, target_date: datetime.date, move_rows: list[dict]) -> None:
    session.query(Move).filter(Move.snapshot_date == target_date).delete()

    if move_rows:
        session.execute(insert(Move), move_rows)
        
# label gainer or loser or spike
def label(target_date: datetime.date, pct_changes: dict, volume_ratios: dict) -> list[dict]:
    gainers, losers = rank_top_movers(pct_changes)
    spikes = find_volume_spikes(volume_ratios)
    move_rows = []
    for symbol, value in gainers:

        move_rows.append({"snapshot_date": target_date, "ticker_symbol": symbol, "move_type": "top_gainer", "value": value})
        
    for symbol, value in losers:
        move_rows.append({"snapshot_date": target_date, "ticker_symbol": symbol, "move_type": "top_loser", "value": value})
    for symbol, value in spikes:
        move_rows.append({"snapshot_date": target_date, "ticker_symbol": symbol, "move_type": "volume_spike", "value": value})
    return move_rows


def main() -> None:
    session = SessionLocal()
    try:
        target_date = lastprice_date(session)
        if target_date is None:
            print("No price data found. run fetch_prices.")
            return

        pct_changes = {}
        volume_ratios = {}

        for symbol in WATCHLIST:
            history = price_hist(session, symbol)
            if not history:
                continue  # not fetched yet

            metrics = compute_ticker_metrics(history, target_date)
            if metrics is None:
                continue  

            if metrics["pct_change"] is not None:
                pct_changes[symbol] = metrics["pct_change"]
                
            if metrics["volume_ratio"] is not None:
                volume_ratios[symbol] = metrics["volume_ratio"]

        move_rows = label(target_date, pct_changes, volume_ratios)
        upsert_snapshot(session, target_date)
        replaceMoves_date(session, target_date, move_rows)
        session.commit()

        print(f"Computed {len(move_rows)} moves for {target_date}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
