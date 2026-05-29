#!/usr/bin/env python3
"""Fast Research: Search web for sources on a topic."""
import sys, json, re, urllib.parse, subprocess, os, tempfile

TAVILY_AVAILABLE = True  # Use tvly CLI (pre-configured with API key)

def search_tavily(query, max_results=10):
    """Use tvly CLI for search."""
    try:
        tmpfile = os.path.join(tempfile.gettempdir(), f"tavily_{os.getpid()}.json")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            ["tvly", "search", query, "--max-results", str(max_results), "--json", "-o", tmpfile],
            capture_output=True, text=True, timeout=30, env=env
        )
        if os.path.exists(tmpfile):
            with open(tmpfile, encoding='utf-8') as f:
                results = json.load(f)
            os.remove(tmpfile)
        else:
            return search_duckduckgo(query, max_results)

        formatted = []
        for item in results.get("results", []):
            url = item.get("url", "")
            domain = re.search(r"https?://([^/]+)", url)
            domain = domain.group(1) if domain else "unknown"

            file_type = "webpage"
            if url.endswith(".pdf") or "/pdf" in url:
                file_type = "pdf"
            elif "youtube.com" in domain or "youtu.be" in domain:
                file_type = "video"

            credibility = 3
            high_cred = ["arxiv.org", "ieee.org", "acm.org", "nature.com",
                        "science.org", "mit.edu", "stanford.edu", "harvard.edu",
                        "wikipedia.org", "ibm.com", "google.com", "microsoft.com"]
            low_cred = ["blogspot.com", "medium.com", "reddit.com", "quora.com"]

            if any(d in domain for d in high_cred):
                credibility = 5
            elif any(d in domain for d in low_cred):
                credibility = 2

            formatted.append({
                "title": item.get("title", "Untitled"),
                "url": url,
                "domain": domain,
                "type": file_type,
                "summary": item.get("content", "")[:200],
                "credibility": credibility
            })
        return formatted
    except Exception as e:
        return search_duckduckgo(query, max_results)

def search_duckduckgo(query, max_results=10):
    """Fallback search using DuckDuckGo HTML."""
    import requests
    from bs4 import BeautifulSoup

    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for result in soup.select(".result")[:max_results]:
            a = result.select_one(".result__a")
            if not a:
                continue

            title = a.get_text(strip=True)
            href = a.get("href", "")

            snippet = ""
            snippet_elem = result.select_one(".result__snippet")
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)

            domain = re.search(r"https?://([^/]+)", href)
            domain = domain.group(1) if domain else "unknown"

            file_type = "webpage"
            if href.endswith(".pdf") or "/pdf" in href:
                file_type = "pdf"
            elif "youtube.com" in domain or "youtu.be" in domain:
                file_type = "video"

            credibility = 3
            high_cred = ["arxiv.org", "ieee.org", "acm.org", "nature.com",
                        "science.org", "mit.edu", "stanford.edu", "harvard.edu",
                        "wikipedia.org", "ibm.com", "google.com", "microsoft.com"]
            low_cred = ["blogspot.com", "medium.com", "reddit.com", "quora.com"]

            if any(d in domain for d in high_cred):
                credibility = 5
            elif any(d in domain for d in low_cred):
                credibility = 2

            results.append({
                "title": title,
                "url": href,
                "domain": domain,
                "type": file_type,
                "summary": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                "credibility": credibility
            })

        return results
    except Exception as e:
        return [{"error": str(e), "fallback": "Search failed"}]

def format_results(results, topic):
    """Format results for user display."""
    output = {
        "topic": topic,
        "mode": "fast",
        "count": len(results),
        "sources": []
    }

    for i, r in enumerate(results, 1):
        type_emoji = {"pdf": "[PDF]", "webpage": "[WEB]", "video": "[VIDEO]"}.get(r.get("type", "webpage"), "[WEB]")
        stars = "*" * r.get("credibility", 3)

        output["sources"].append({
            "id": i,
            "title": r.get("title", "Untitled"),
            "url": r.get("url", ""),
            "domain": r.get("domain", "unknown"),
            "type": r.get("type", "webpage"),
            "summary": r.get("summary", ""),
            "credibility": r.get("credibility", 3),
            "display": f"[{i}] {type_emoji} {r.get('title', 'Untitled')} ({r.get('type', 'webpage')})\n    Domain: {r.get('domain', 'unknown')} | Credibility: {stars}\n    Summary: {r.get('summary', 'N/A')[:150]}"
        })

    return output

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    query = sys.argv[1] if len(sys.argv) > 1 else "machine learning"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    # Try Tavily first if available
    if TAVILY_AVAILABLE:
        results = search_tavily(query, max_results)
    else:
        results = search_duckduckgo(query, max_results)

    formatted = format_results(results, query)
    print(json.dumps(formatted, ensure_ascii=False, indent=2))