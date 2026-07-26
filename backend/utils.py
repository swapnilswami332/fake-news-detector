from urllib.parse import urlparse


TRUSTED_DOMAINS = (
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "who.int",
    "cdc.gov",
    "gov",
    "edu",
)


def clean_sources(results: list[dict], limit: int = 4) -> list[dict[str, str]]:
    sources = []
    seen_urls = set()

    for result in results:
        url = result.get("href") or result.get("url") or ""
        title = result.get("title") or ""
        if not url.startswith(("https://", "http://")) or not title or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append({"title": title.strip()[:180], "url": url})
        if len(sources) == limit:
            break
    return sources


def is_trusted_source(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in TRUSTED_DOMAINS)


def calculate_trust_score(
    prediction: str, confidence: int, sources: list[dict[str, str]]
) -> int:
    trusted_count = sum(is_trusted_source(source["url"]) for source in sources)
    source_signal = min(trusted_count * 12, 36)
    prediction_signal = confidence if prediction == "Real" else 100 - confidence
    return max(5, min(95, round(prediction_signal * 0.64 + source_signal)))
