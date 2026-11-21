import csv
import os
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed" / "AAPL_FY2026"
RAW = ROOT / "data" / "raw" / "AAPL"

load_dotenv(ROOT / ".env")
DSN = (
    f"host={os.environ['POSTGRES_HOST']} "
    f"port={os.environ['POSTGRES_PORT']} "
    f"dbname={os.environ['POSTGRES_DB']} "
    f"user={os.environ['POSTGRES_USER']} "
    f"password={os.environ['POSTGRES_PASSWORD']}"
)

FY2026_ACCESSION = "0000320193-26-000026"
METRICS = ["total_net_sales", "total_cost_of_sales", "gross_margin"]

def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def load_company(cur):
    cur.execute(
        """INSERT INTO companies (ticker, name, cik)
           VALUES (%s, %s, %s)
           ON CONFLICT (ticker) DO NOTHING""",
        ("AAPL", "Apple Inc.", "0000320193"),
    )    

def load_filing(cur, row):
    cur.execute(
        """INSERT INTO filings (ticker, accession, fiscal_year, period_end, filed_date, source_url)
           VALUES (%s, %s, %s, %s, %s, %s)
           ON CONFLICT (accession) DO NOTHING""",
        ("AAPL", row["accession"], int(row["fiscal_year"]),
         row["period_end"], row["filed"], row["url"]),
    )
    cur.execute("SELECT id FROM filings WHERE accession = %s", (row["accession"],))
    return cur.fetchone()[0]

def load_sections(cur, filing_id):
    rows = read_csv(PROCESSED / "sections.csv")
    for row in rows:
        cur.execute(
            """INSERT INTO sections (filing_id, item, title, start_page, end_page)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (filing_id, item) DO NOTHING""",
            (filing_id, row["item"], row["title"],
             int(row["start_page"]), int(row["end_page"])),
        )
    return len(rows)

def load_facts(cur, filing_id):
    rows = read_csv(PROCESSED / "income_statement.csv")
    count = 0
    for row in rows:
        for metric in METRICS:
            cur.execute(
                """INSERT INTO financial_facts
                       (filing_id, metric, fiscal_year, value, units, source_table)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (filing_id, metric, fiscal_year) DO NOTHING""",
                (filing_id, metric, int(row["fiscal_year"]),
                 Decimal(row[metric]), row["units"], "income statement"),
            )
            count += 1
    return count

def main():
    manifest = read_csv(RAW / "manifest.csv")
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            load_company(cur)
            filing_ids = {row["accession"]: load_filing(cur, row) for row in manifest}
            fy26_id = filing_ids[FY2026_ACCESSION]
            n_sections = load_sections(cur, fy26_id)
            n_facts = load_facts(cur, fy26_id)
    print(f"Filings loaded: {len(filing_ids)}")
    print(f"Sections processed: {n_sections}")
    print(f"Financial facts processed: {n_facts}")


if __name__ == "__main__":
    main()