import csv 
from pathlib import Path
from edgar import get, get_cik, list_10k

TICKER="AAPL"
FISCAL_YEARS=3
RAW_PATH=Path(__file__).resolve().parents[2] / "data" / "raw"

def download_filing(filing: dict, folder_path: Path) -> Path:
    path = folder_path / f"{filing['accession']}{Path(filing['url']).suffix}"
    if path.exists():
        print(f"{path.name} already exists")
    else:
        path.write_bytes(get(filing["url"]).content)
    return path
def download_companyfacts(cik: str, folder_path: Path) -> Path:
    path = folder_path / "companyfacts.json"
    if not path.exists():
        path.write_bytes(get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json").content)
    return path

def write_manifest(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cik = get_cik(TICKER)
    filings = list_10k(cik)[:FISCAL_YEARS]
    folder_path = RAW_PATH / TICKER
    folder_path.mkdir(parents=True, exist_ok=True)

    rows = []
    for f in filings:
        path = download_filing(f, folder_path)
        print(f"saved FY{f['fiscal_year']} -> {path.name} ({path.stat().st_size:,} bytes)")
        rows.append({**f, "local_path": str(path), "bytes": path.stat().st_size})

    facts = download_companyfacts(cik, folder_path)
    print(f"company facts -> {facts.name} ({facts.stat().st_size:,} bytes)")

    write_manifest(rows, folder_path / "manifest.csv")
    print(f"manifest written: {len(rows)} filings")


if __name__ == "__main__":
    main()