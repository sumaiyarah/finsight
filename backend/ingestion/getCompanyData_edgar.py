import requests 
Headers ={"User-Agent": "FinSight learning project sumaiya.sadiarahman@gmail.com"}

def get_cik(ticker:str) -> str:
    r=requests.get("https://www.sec.gov/files/company_tickers.json",headers=Headers,timeout=30)
    r.raise_for_status()
    for entry in r.json().values():
        if entry["ticker"].upper() == ticker.upper():
            return str (entry["cik_str"]).zfill(10)
    raise ValueError(f"Ticker {ticker} not found")

def list_10ks(cik:str)-> list[dict]:
    r=requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json",headers=Headers,timeout=30)
    r.raise_for_status()
    recent=r.json()["filings"]["recent"]
    filings=[]
    for form, acc, filed, period, doc in zip(recent["form"], recent["accessionNumber"],
                                             recent["filingDate"], recent["reportDate"],
                                             recent["primaryDocument"]):
        if form == "10-K":
            folder = acc.replace("-", "")
            filings.append({"accession": acc, "filed": filed, "period_end": period,
                            "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{folder}/{doc}"})
    return filings

if __name__ == "__main__":
    cik = get_cik("AAPL")
    print("Apple CIK:", cik)
    for f in list_10ks(cik)[:3]:
        print(f)
