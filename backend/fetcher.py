import time
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

USER_AGENT = "KnowledgeAssistantBot/0.1 (learning project)"

def allowed_by_robots(url: str) -> bool:
    p = urlparse(url)
    rp = RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    rp.read()
    return rp.can_fetch(USER_AGENT, url)

def fetch(url: str, delay: float = 1.0) -> str | None:
    if not allowed_by_robots(url):
        print("blocked by robots.txt:", url)
        return None
    time.sleep(delay)                              
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    except requests.RequestException as e:
        print("request failed:", e)
        return None
    if r.status_code != 200:
        print("status", r.status_code, "for", url)
        return None
    return r.text

if __name__ == "__main__":
    html = fetch("https://quotes.toscrape.com/")
    print(len(html) if html else "no page")
    print(html[:200] if html else "")