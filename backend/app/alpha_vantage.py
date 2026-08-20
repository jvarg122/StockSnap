import datetime

import requests

from app.config import ALPHA_VANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageError(Exception):
    pass


def fetch_daily_series(symbol: str) -> dict[datetime.date, dict]:
    response = requests.get(
        BASE_URL,
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": ALPHA_VANTAGE_API_KEY,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    if "Note" in payload:
        raise AlphaVantageError(f"rate limited while fetching {symbol}: {payload['Note']}")
    if "Error Message" in payload:
        raise AlphaVantageError(f"bad symbol {symbol}: {payload['Error Message']}")

    series = payload.get("Time Series (Daily)")
    if not series:
        raise AlphaVantageError(f"unexpected response shape for {symbol}: {payload}")

    return {
        datetime.date.fromisoformat(date_str): {
            "close": float(day["4. close"]),
            "volume": int(day["5. volume"]),
        }
        for date_str, day in series.items()
    }
