import datetime
from fastapi.testclient import TestClient
from app.models import Move
from scripts.compute_moves import upsert_snapshot
from scripts.fetch_prices import upsert_ticker
from sqlalchemy import insert
from app.main import app

client = TestClient(app)
#empty list
def test_empty(db_session):
    response = client.get("/api/snapshots")
    assert response.status_code == 200
    assert response.json() == []

#no data yet
def test_none(db_session):
    response = client.get("/api/snapshots/latest")
    assert response.status_code == 404


def test_missingDate(db_session): # date doesn't exist
    response = client.get("/api/snapshots/2026-01-01")
    assert response.status_code == 404