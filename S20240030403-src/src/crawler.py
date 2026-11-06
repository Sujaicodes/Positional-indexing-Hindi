"""Polite, domain-limited crawler for Hindi HTML pages.

The crawler saves extracted page text as UTF-8 .txt files and records source URLs.
Respect each website's robots.txt, terms, rate limits and copyright policy.
"""
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from pathlib import Path
import json, time, re, argparse
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "HindiPositionalIndexer/1.0 (educational research; contact: student)"}

def allowed(url):
    p = urlparse(url)
    robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return False  # fail closed if robots policy cannot be checked

def crawl(seed_urls, out_dir, max_pages=20, delay=1.5):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    queue = list(dict.fromkeys(seed_urls))
    seen, sources = set(), {}
    session = requests.Session()
    while queue and len(seen) < max_pages:
        url = queue.pop(0)
        if url in seen or not allowed(url):
            continue
        seen.add(url)
        try:
            response = session.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                tag.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else url
            text = soup.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            # Retain pages with a meaningful amount of Devanagari text.
            if len(re.findall(r"[\u0900-\u097F]", text)) < 100:
                continue
            name = f"crawl_{len(sources)+1:04d}.txt"
            (out / name).write_text(title + "\n" + text, encoding="utf-8")
            sources[name] = url
            for link in soup.find_all("a", href=True):
                target = urljoin(url, link["href"]).split("#")[0]
                parsed = urlparse(target)
                if parsed.scheme in ("http", "https") and parsed.netloc == urlparse(url).netloc and target not in seen:
                    if target not in queue:
                        queue.append(target)
        except requests.RequestException as exc:
            print(f"[skip] {url}: {exc}")
        time.sleep(delay)
    (out.parent / "sources_crawled.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(sources)} Hindi pages in {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", required=True)
    parser.add_argument("--out", default="dataset/crawled")
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--delay", type=float, default=1.5)
    args = parser.parse_args()
    crawl(args.seeds, args.out, args.max_pages, args.delay)
