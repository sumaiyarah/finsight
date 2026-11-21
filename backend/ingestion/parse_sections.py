import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
FILING = ROOT / "data" / "raw" / "AAPL" / "0000320193-26-000026.htm"
OUT_DIR = ROOT / "data" / "processed" / "AAPL_FY2026"

FOOTER_RE = re.compile(r"Inc\. \| 2026 Form 10-K \| (\d+)")
HEADING_RE = re.compile(r"^Item\s+(\d+[A-Z]?)\.\s+\S")
BOLD_RE = re.compile(r"font-weight:\s*700")

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def find_headings(soup):
    headings = []
    seen = set()
    for el in soup.find_all(style=BOLD_RE):
        first = el.find(string=True)
        if id(first) in seen:  # nested bold element: same heading, already counted
            continue
        seen.add(id(first))
        text = normalise(el.get_text(" "))
        match = HEADING_RE.match(text)
        if match:
            title = re.sub(r"^Item\s+\S+?\.\s*", "", text)
            headings.append({"item": match.group(1), "title": title, "el": el})
    return headings

def page_of(el) -> int:
    footer = el.find_next(string=FOOTER_RE)
    return int(FOOTER_RE.search(footer).group(1))

def section_text(strings, start, end):
    pieces = []
    for s in strings[start:end]:
        t = normalise(s)
        if t and not FOOTER_RE.search(t):
            pieces.append(t)
    return " ".join(pieces)

def main() -> None:
    soup = BeautifulSoup(FILING.read_bytes(), "xml")
    strings = list(soup.find_all(string=True))
    position = {id(s): i for i, s in enumerate(strings)}
    headings = find_headings(soup)
    
    footer_texts = soup.find_all(string=FOOTER_RE)
    if not footer_texts:
        raise ValueError("No page footers found. Check FOOTER_RE and the filing file.")
    last_page = max(int(FOOTER_RE.search(t).group(1)) for t in footer_texts)
    rows = []
    for k, h in enumerate(headings):
        start = position[id(h["el"].find(string=True))]
        if k + 1 < len(headings):
            nxt = headings[k + 1]["el"]
            end = position[id(nxt.find(string=True))]
            end_page = page_of(nxt)
        else:
            end = len(strings)
            end_page = last_page
        
        text = section_text(strings, start, end)
        print("Texts:",text)
        rows.append({
            "item": h["item"],
            "title": h["title"],
            "start_page": page_of(h["el"]),
            "end_page": end_page,
            "chars": len(text),
            "text": text,
        })
        
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text_dir = OUT_DIR / "sections"
    text_dir.mkdir(exist_ok=True)
    for r in rows:
        (text_dir / f"Item_{r['item']}.txt").write_text(r["text"], encoding="utf-8")
    fields = ["item", "title", "start_page", "end_page", "chars"]
    with open(OUT_DIR / "sections.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    items = [r["item"] for r in rows]
    pages = [r["start_page"] for r in rows]
    print(f"headings found: {len(rows)}")
    print("items unique:", len(items) == len(set(items)))
    print("start pages never decrease:", pages == sorted(pages))
    for r in rows:
        print(f"Item {r['item']:<4} pages {r['start_page']:>2}-{r['end_page']:<2} "
            f"{r['chars']:>8,} chars  {r['title'][:45]}")


if __name__ == "__main__":
    main()