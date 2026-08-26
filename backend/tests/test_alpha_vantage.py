import datetime
import pytest
from unittest.mock import Mock, patch
from app.alpha_vantage import AlphaVantageError, fetch_daily_series

def make_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response

#tests
@patch("app.alpha_vantage.requests.get")
def parses_close_volume(mock_get):
    mock_get.return_value = make_response({
        "Time Series (Daily)": {
            "2026-08-14": {"4. close": "230.5000", "5. volume": "42000000"},

            "2026-08-13": {"4. close": "228.1000", "5. volume": "39000000"},
        }
    })

    series = fetch_daily_series("AAPL")
    assert series[datetime.date(2026, 8, 14)] == {"close": 230.5, "volume": 42000000}

    assert series[datetime.date(2026, 8, 13)] == {"close": 228.1, "volume": 39000000}


@patch("app.alpha_vantage.requests.get")
def rate_limit_testing(mock_get):
    mock_get.return_value = make_response({"hit request limit"})

    with pytest.raises(AlphaVantageError, match="rate limited"):
        fetch_daily_series("AAPL")

# someone typed a typo or an invalid ticker.
@patch("app.alpha_vantage.requests.get")
def test_invalid_ticker(mock_get):
    mock_get.return_value = make_response({"Error Message": "Invalid API call"})

    with pytest.raises(AlphaVantageError, match="bad symbol"):
        fetch_daily_series("FAKESYMBOL")
