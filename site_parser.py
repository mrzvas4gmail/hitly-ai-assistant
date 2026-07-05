import requests
from bs4 import BeautifulSoup


def fetch_site_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    headings = []
    for h in soup.find_all(["h1", "h2", "h3"]):
        text = h.get_text(" ", strip=True)
        if text:
            headings.append(text)

    body_text = soup.get_text(" ", strip=True)

    result = f"""
Заголовок сайта:
{title}

Заголовки:
{chr(10).join(headings[:20])}

Текст страницы:
{body_text[:6000]}
"""

    return result
