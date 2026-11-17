import time 
import requests

HEADERS={"User-Agent":"FinSight learning project sumaiya.sadiarahman@gmail.com"}
PAUSE_SECONDS=0.2

def get(url:str) -> requests.Response:
    time.sleep(PAUSE_SECONDS)
    r=requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r

def get_cik(ticker:str) -> str:
    for entry in get("https://www.sec.gov/files/company_tickers.json").json().values():
        if entry["ticker"].upper()==ticker.upper():
            return str(entry["cik_str"]).zfill(10)
    raise ValueError (f"Ticker {ticker} not found")

def list_10k(cik:str) -> str :
    filings=[]
    recent = get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()["filings"]["recent"]
    for form, acc, filed, period, doc in zip(recent["form"],recent["accessionNumber"],recent["filingDate"],recent["reportDate"],
                                             recent["primaryDocument"]):
        if form == "10-K":
            folder= acc.replace("-","")
            filings.append({
                "accession": acc,
                "filed": filed,
                "period_end": period,
                "fiscal_year": period[:4], 
                "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{folder}/{doc}",
            })
    return filings