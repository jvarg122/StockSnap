import datetime
import requests

# SEC required
USER_AGENT = "Josue Vargas vargasjosuedev@gmail.com"

company_tickers = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

cik = None

def cik_lookup():
    global cik

    #if we have the data use it
    if cik is not None:
        return cik

# download company ticker data
    response = requests.get(
        company_tickers,
        headers={"User-Agent": USER_AGENT}, 
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    #dict of ticker
    cik = {}

    for company in data.values():
        ticker = company["ticker"].upper()
        cik_num = str(company["cik_str"]).zfill(10)

        cik[ticker] = cik_num

    return cik


def get_cik(symbol: str) -> str | None:
    # look up company's cik num
    symbol = symbol.upper()

    return cik_lookup().get(symbol)

def get_latestFilings(symbol: str) -> list[dict]:
    cik = get_cik(symbol)
    if cik is None:
        return []

    url = SUBMISSIONS_URL.format(cik=cik)

    response = requests.get(
        url, 
        headers={"User-Agent": USER_AGENT}, 
        timeout=10
    )

    response.raise_for_status() #error check

    data = response.json()

    recent = data["filings"]["recent"]

    forms = recent["form"]
    dates = recent["filingDate"]

    filings = []

    for form, date in zip(forms, dates):
        filing = {
            "form": form,
            "filed_date": date
        }
        filings.append(filing)

    return filings

def get_filingsNear(symbol: str, target_date: datetime.date, days_window: int = 1) -> list[dict]:

    filings = get_latestFilings(symbol)

    nearDateFilings = []
    for f in filings:
        filing_date = datetime.date.fromisoformat(f["filed_date"])

        days_apart = abs((filing_date - target_date).days)
        if days_apart <= days_window:
            nearDateFilings.append(f)

    return nearDateFilings