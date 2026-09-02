import datetime
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.move_explainer import ExplainError, explain_move
from app.db import SessionLocal
from app.models import Move, Snapshot, Ticker
from app.sec_edgar import get_filingsNear

app = FastAPI(title="Stock Snap API")

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


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
            "sector": ticker.sector,
            "move_type": move.move_type,
            "value": float(move.value),
        })

    return moves


@app.get("/api/snapshots")
def list_snapshots(db: Session = Depends(get_db)):
    snapshots = (
        db.query(Snapshot.date)
        .order_by(Snapshot.date.desc())
        .all()
    )
    return [snapshot[0] for snapshot in snapshots]


# today gainers, losers, spikes
@app.get("/api/snapshots/latest")
def latest_snapshot(db: Session = Depends(get_db)):
    latest_date = db.query(func.max(Snapshot.date)).scalar()

    if latest_date is None:
        raise HTTPException(
            status_code=404,
            detail="No snapshots found"
        )

    return {
        "date": latest_date,
        "moves": get_moves_for_date(db, latest_date),
    }


# for specific day
@app.get("/api/snapshots/{target_date}")
def get_snapshot(target_date: datetime.date, db: Session = Depends(get_db)):
    snapshot = db.get(Snapshot, target_date)

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"No snapshot for {target_date}"
        )
    return {
        "date": target_date,
        "moves": get_moves_for_date(db, target_date),
    }


# OpenAI call when someone clicks on a specific ticker
@app.get("/api/explain/{target_date}/{symbol}")
def explain(target_date: datetime.date, symbol: str, db: Session = Depends(get_db)):
    move = (
        db.query(Move)
        .filter(Move.snapshot_date == target_date, Move.ticker_symbol == symbol)
        .first()
    )
    if move is None:
        raise HTTPException(status_code=404, detail=f"No move for {symbol} on {target_date}")

    ticker = db.get(Ticker, symbol)
    filings = get_filingsNear(symbol, target_date)

    try:
        explanation = explain_move(
            symbol, ticker.name, ticker.sector, move.move_type, float(move.value), filings
        )
    except ExplainError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "explanation": explanation,
        "disclaimer": "StockSnap Analysis. Review recommended.",
        "filings": filings,
    }
