from fetcher import fetch
from cleaner import clean_html
from change_detector import has_changed, record
from ingest import ingest

def process_url(url: str) -> str:
    html = fetch(url)
    if html is None:
        return "fetch_failed"
    cleaned = clean_html(html)
    if not cleaned:
        return "empty_page"
    if not has_changed(url, cleaned):
        return "unchanged"
    n = ingest(url, cleaned)          
    if n == 0:
        return "empty_page"
    record(url, cleaned)               
    return f"ingested {n} chunks"

if __name__ == "__main__":
    import sys
    print(process_url(sys.argv[1]))