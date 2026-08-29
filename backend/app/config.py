import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.environ["ALPHA_VANTAGE_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

WATCHLIST = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
    "DIS",
    "JPM",
    "V",
    "JNJ",
    "PFE",
    "WMT",
    "KO",
    "XOM",
    "BA",
    "COIN",
    "INTC",
]

TICKER_INFO = {
    "AAPL": {"name": "Apple", "sector": "Technology"},
    "MSFT": {"name": "Microsoft", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet", "sector": "Technology"},
    "AMZN": {"name": "Amazon", "sector": "Consumer Discretionary"},
    "NVDA": {"name": "Nvidia", "sector": "Technology"},
    "META": {"name": "Meta Platforms", "sector": "Technology"},
    "TSLA": {"name": "Tesla", "sector": "Consumer Discretionary"},
    "AMD": {"name": "Advanced Micro Devices", "sector": "Technology"},
    "NFLX": {"name": "Netflix", "sector": "Communication Services"},
    "DIS": {"name": "Walt Disney", "sector": "Communication Services"},
    "JPM": {"name": "JPMorgan Chase", "sector": "Financials"},
    "V": {"name": "Visa", "sector": "Financials"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare"},
    "PFE": {"name": "Pfizer", "sector": "Healthcare"},
    "WMT": {"name": "Walmart", "sector": "Consumer Staples"},
    "KO": {"name": "Coca-Cola", "sector": "Consumer Staples"},
    "XOM": {"name": "Exxon Mobil", "sector": "Energy"},
    "BA": {"name": "Boeing", "sector": "Industrials"},
    "COIN": {"name": "Coinbase", "sector": "Financials"},
    "INTC": {"name": "Intel", "sector": "Technology"},
}
