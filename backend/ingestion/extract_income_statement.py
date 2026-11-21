import re 
from pathlib import Path
import pandas as pd

FILING = Path(__file__).resolve().parents[2] / "data" / "raw" / "AAPL" / "0000320193-26-000026.htm"
     
YEARS = ["2026", "2025", "2024"] 


def find_rows(df, label):
    """Return every row that contains the label text."""
    rows = []
    for _, row in df.iterrows():
        texts = [re.sub(r"\s+", " ", str(c)) for c in row if pd.notna(c)]
        if any(label in t for t in texts):
            rows.append(row)
    
    return rows


def table_has(df, label):
    return bool(find_rows(df, label))


def find_income_table(tables):
    labels = ["Total net sales", "Total cost of sales", "Gross margin"]
    matches = [i for i, df in enumerate(tables)
               if all(table_has(df, label) for label in labels)]
    if len(matches) != 1:
        raise ValueError(f"Expected 1 income statement table, found {len(matches)}: {matches}")
    print(f"income statement is table {matches[0]}")
    return tables[matches[0]] 

def numbers_in(row):
    """Keep only numeric cells, and collapse the copies that merged cells create."""
    values = []
    for cell in row:
        if pd.isna(cell):
            continue
        text = str(cell).strip()
        if not re.fullmatch(r"\(?[\d,]+\)?", text):
            continue                       # skip labels like "Total cost of sales"
        if values and values[-1] == text:  # same number copied into the next column
            continue
        values.append(text)
    return [int(v.replace(",", "").strip("()")) for v in values]

def numbers_for(df, label):
    matches = find_rows(df, label)
    print(f"{label!r}: {len(matches)} matching row(s)")
    
    return numbers_in(matches[0]) if matches else []

OUT_FILE = Path(__file__).resolve().parents[2] / "data" / "processed" / "AAPL_FY2026" / "income_statement.csv"

def save_income_statement(sales, cost, margin):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "company": "Apple",
            "ticker": "AAPL",
            "fiscal_year": year,
            "units": "USD millions",
            "total_net_sales": s,
            "total_cost_of_sales": c,
            "gross_margin": m,
            "check_sales_equals_cost_plus_margin": s == c + m,
        }
        for year, s, c, m in zip(YEARS, sales, cost, margin)
    ]
    pd.DataFrame(rows).to_csv(OUT_FILE, index=False)
    print(f"saved {len(rows)} rows -> {OUT_FILE}")
def main() -> None:
    tables = pd.read_html(FILING)
    df = find_income_table(tables)

    sales = numbers_for(df, "Total net sales")
    cost = numbers_for(df, "Total cost of sales")
    margin = numbers_for(df, "Gross margin")

    for year, s, c, m in zip(YEARS, sales, cost, margin):
        print(f"{year}: net sales {s:,} | cost of sales {c:,} | gross margin {m:,} | "
              f"check (sales = cost + margin): {s == c + m}")
    save_income_statement(sales, cost, margin)

if __name__ == "__main__":
    main()

if __name__=="__main__":
    main()