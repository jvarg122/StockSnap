import datetime
from fastapi import FastAPI, HTTPException
from sqlalchemy import func
from app.db import SessionLocal
from app.models import Move, Snapshot, Ticker

app = FastAPI(title="Stock Snap API")

# gets every move for one day
def get_moves_for_date(session, date):
    results = (
        session.query(Move, Ticker)
        .join(Ticker, Move.ticker_symbol == Ticker.symbol) # attaches company name to each one
        .filter(Move.snapshot_date == date)
        .all()
    )

    moves = []
    for move, ticker in results:
        moves.append({
            "symbol": move.ticker_symbol,
            "name": ticker.name,
            "move_type": move.move_type,
            "value": float(move.value),
        })

    return moves

@app.get("/api/snapshots")
def list_snapshots():
    session = SessionLocal()

    try:
        snapshots = (
            session.query(Snapshot.date)
            .order_by(Snapshot.date.desc())
            .all()
        )
        return [snapshot[0] for snapshot in snapshots]
    finally:
        session.close()

# today gainers, losers, spikes
@app.get("/api/snapshots/latest")
def latest_snapshot():
    session = SessionLocal()
    try:
        latest_date = session.query(func.max(Snapshot.date)).scalar()

        if latest_date is None:
            raise HTTPException(
                status_code=404,
                detail="No snapshots found"
            )
            
        return {
            "date": latest_date,
            "moves": get_moves_for_date(session, latest_date),
        }
    finally:
        session.close()

# for specific day 
@app.get("/api/snapshots/{target_date}")
def get_snapshot(target_date: datetime.date):
    session = SessionLocal()

    try:
        snapshot = session.get(Snapshot, target_date)

        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"No snapshot for {target_date}"
            )
        return {
            "date": target_date,
            "moves": get_moves_for_date(session, target_date),
        }
    finally:
        session.close()
