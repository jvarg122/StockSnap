import datetime
import requests

from app.config import ALPHA_VANTAGE_API_KEY
av_url = "https://www.alphavantage.co/query"


class AlphaVantageError(Exception):
    pass


def fetch_daily_series(symbol: str) -> dict[datetime.date, dict]:
    response = requests.get(
        av_url,
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": ALPHA_VANTAGE_API_KEY,
        },
        timeout=10,
    )
    response.raise_for_status()
    body = response.json()

    if "Note" in body:
        raise AlphaVantageError(f"rate limited while fetching {symbol}: {body['Note']}")
    if "Error Message" in body:
        raise AlphaVantageError(f"bad symbol {symbol}: {body['Error Message']}")

    series = body.get("Time Series (Daily)")
    if not series:
        raise AlphaVantageError(f"unexpected response shape for {symbol}: {body}")

    return {
        datetime.date.fromisoformat(date_str): {
            "close": float(day["4. close"]),
            "volume": int(day["5. volume"]),
        }
        for date_str, day in series.items()
    }
#souce: https://www.alphavantage.co/documentation/
# alphaMarket API News & Sentiment 
def fetch_news(symbol: str, target_date: datetime.date, days_window: int = 1) -> list[dict]:

    window = datetime.timedelta(days=days_window)

    start_date = target_date - window
    end_date = target_date + window

    # YYYYMMDDTHHMM format
    time_from = start_date.strftime("%Y%m%dT0000")
    time_to = end_date.strftime("%Y%m%dT2359") # 23:59 time 11:59 PM

    response = requests.get(
        av_url,
        params={
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "time_from": time_from,
            "time_to": time_to,
            "apikey": ALPHA_VANTAGE_API_KEY,
        },

        timeout=10,
    )
    response.raise_for_status()
    body = response.json()

    if "Note" in body:
        raise AlphaVantageError(
            f"rate limited while fetching news for {symbol}: {body['Note']}"
        )
    if "Information" in body:
        raise AlphaVantageError(
            f"news request rejected for {symbol}: {body['Information']}"
        )

    feed = body.get("feed", [])

    articles = []

    for item in feed:
        article = {
            "title": item["title"],
            "url": item["url"],
            "source": item["source"],
            "published": item["time_published"],
            "sentiment": item.get("overall_sentiment_label"),
        }
        articles.append(article)

    return articles
