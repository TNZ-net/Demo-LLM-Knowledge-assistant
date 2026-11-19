from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()                    
    text = soup.get_text(separator=" ")     
    return " ".join(text.split())           

if __name__ == "__main__":
    from fetcher import fetch
    html = fetch("https://quotes.toscrape.com/")
    if html:
        out = clean_html(html)
        print("before:", len(html), "after:", len(out))
        print(out[:300])