# Stock Snap

**StockSnap** is a tool that looks at stock prices every day and shows you a daily snap shot of interesting stock moves. StockSnap uses uses a scheduled cron job to fetch and compute real-time market data triggered daily, an AI agent tool-calling loop using real time market data (SEC filings, price trend, sector context, news) to explain moves across your ticker watchlist (e.g., top gainer/top losers/volume spikes/relative performance) with the results displayed in a dashboard.

Deployed: http://34.217.43.40


## Architecture

<img src="https://i.imgur.com/xisHPqp.png" width="400">

## Stack

**Backend:** FastAPI, PostgreSQL, Alpha Vantage, OpenAI API (used for tool-calling agent), pytest

**Frontend:** React + Vite, CSS, TradingView widgets

**Infrastructure:** AWS (EC2, RDS), Nginx, cron

## Project structure Overview

```
stock-snap/
├── backend/
│   ├── app/
│   │   ├── main.py               FastAPI routes
│   │   ├── models.py             models (Ticker, DailyPrice, Snapshot, Move)
│   │   ├── moves.py              move logic (e.g., gainers/losers/spikes/relative performance)
│   │   ├── move_explainer.py     AI tool-calling agent
│   │   ├── move_context.py       price trend/sector context helpers
│   │   ├── alpha_vantage.py      API client
│   │   └── sec_edgar.py          Filings client
│   ├── scripts/                  fetch_prices.py, compute_moves.py, init_db.py 
│   └── tests/                    pytest
│
└── frontend/
    └── src/
        ├── App.jsx               dashboard
        ├── HomePage.jsx          homepage
        └── widgets/             
```

## API

| Method | Route | Description |
|---|---|---|
| `GET` | `/api/snapshots` | List all available snapshot dates |
| `GET` | `/api/snapshots/latest` | Get moves for the most recent snapshot |
| `GET` | `/api/snapshots/{date}` | Get moves for a specific date |
| `GET` | `/api/explain/{date}/{symbol}` | Explanation for a specific move |


## Running it locally

**Prerequisites:** Python, Node.js, PostgreSQL

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate       
pip install -r requirements.txt
cp .env.example .env           
python -m scripts.init_db
python -m scripts.fetch_prices
python -m scripts.compute_moves
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Requires API keys from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and an [OpenAI API key](https://platform.openai.com/api-keys) set in `backend/.env`.

## Testing

```bash
cd backend
pytest
```
No API costs during test runs.
