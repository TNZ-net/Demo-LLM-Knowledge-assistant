from pipeline import process_url

def load_sources(path: str = "sources.txt") -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f]
    return [l for l in lines if l and not l.startswith("#")]

def run(path: str = "sources.txt") -> dict[str, str]:
    results = {}
    for url in load_sources(path):
        try:
            results[url] = process_url(url)
        except Exception as e:                 
            results[url] = f"error: {e}"
    return results

if __name__ == "__main__":
    for url, status in run().items():
        print(f"{status:22} {url}")