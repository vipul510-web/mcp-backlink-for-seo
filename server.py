#!/usr/bin/env python3
"""
Backlink MCP Server
Free backlink discovery using DuckDuckGo, Wayback Machine, and web scraping.
"""

import json
import re
import time
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("backlink-mcp")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _clean_domain(domain: str) -> str:
    """Strip protocol and www from a domain string."""
    domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
    return domain.replace("www.", "")


@mcp.tool()
def find_mentions(domain: str, max_results: int = 20) -> str:
    """
    Find web pages that mention a domain (linked or unlinked).

    Use this to discover:
    - Unlinked brand mentions (outreach opportunities)
    - Sites already linking to you
    - Press coverage and references

    Args:
        domain: The domain to search for (e.g. "example.com")
        max_results: Number of results to return (max 50)
    """
    domain = _clean_domain(domain)
    query = f'"{domain}" -site:{domain}'
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=min(max_results, 50)):
                results.append({
                    "url": r.get("href", ""),
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
        time.sleep(1.5)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "query": query,
        "count": len(results),
        "results": results,
        "next_step": "Run verify_page_links on each URL to check if the mention includes an actual link.",
    }, indent=2)


@mcp.tool()
def find_prospects(niche: str, query_type: str = "write_for_us", max_results: int = 20) -> str:
    """
    Find link-building prospects in a niche.

    Args:
        niche: Topic or industry (e.g. "personal finance", "SaaS marketing")
        query_type: One of:
            - "write_for_us"   — blogs accepting guest posts
            - "guest_post"     — sites with guest post sections
            - "resource_page"  — curated resource/link pages
            - "roundup"        — weekly roundup or best-of posts
        max_results: Number of results to return (max 50)
    """
    queries = {
        "write_for_us": f'{niche} "write for us"',
        "guest_post": f'{niche} "guest post" "submit" OR "contribute"',
        "resource_page": f'{niche} "useful resources" OR "helpful links" OR "recommended tools"',
        "roundup": f'{niche} "weekly roundup" OR "best of the week" OR "top posts"',
    }
    query = queries.get(query_type, queries["write_for_us"])
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=min(max_results, 50)):
                results.append({
                    "url": r.get("href", ""),
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
        time.sleep(1.5)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "query": query,
        "query_type": query_type,
        "count": len(results),
        "results": results,
        "next_step": "Run extract_contact_info on promising URLs to find the site owner's email.",
    }, indent=2)


@mcp.tool()
def find_competitor_link_sources(competitor_domain: str, max_results: int = 20) -> str:
    """
    Find sites that mention or link to a competitor.

    Sites linking to competitors are prime outreach targets —
    they've already shown interest in your niche.

    Args:
        competitor_domain: Competitor's domain (e.g. "competitor.com")
        max_results: Number of results to return (max 50)
    """
    competitor_domain = _clean_domain(competitor_domain)
    query = f'"{competitor_domain}" -site:{competitor_domain}'
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=min(max_results, 50)):
                results.append({
                    "url": r.get("href", ""),
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
        time.sleep(1.5)
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "competitor": competitor_domain,
        "count": len(results),
        "results": results,
        "next_step": "Run verify_page_links on each URL with your own domain to check if they already link to you too.",
    }, indent=2)


@mcp.tool()
def verify_page_links(url: str, target_domain: str) -> str:
    """
    Scrape a page and check whether it links to a target domain.

    Returns:
    - Whether the page is linked or unlinked
    - The exact anchor texts and hrefs found
    - Any emails or contact pages discovered on the page

    Args:
        url: Page URL to scrape
        target_domain: Domain you want to check for links to (e.g. "yourdomain.com")
    """
    target = _clean_domain(target_domain)
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except Exception as e:
        return json.dumps({"error": str(e), "url": url})

    soup = BeautifulSoup(resp.text, "lxml")

    found_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if target in href:
            found_links.append({
                "href": href,
                "anchor_text": a.get_text(strip=True),
            })

    emails = list(set(re.findall(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resp.text
    )))
    emails = [e for e in emails if not any(
        ext in e for ext in [".png", ".jpg", ".svg", ".gif", ".css", ".js"]
    )]

    contact_pages = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"].lower()
        if any(w in text or w in href for w in ["contact", "about", "write-for-us", "contribute", "advertise"]):
            full = a["href"] if a["href"].startswith("http") else urljoin(url, a["href"])
            contact_pages.append({"text": a.get_text(strip=True), "url": full})

    is_linked = len(found_links) > 0
    return json.dumps({
        "url": url,
        "target_domain": target_domain,
        "is_linked": is_linked,
        "status": "already links to you" if is_linked else "unlinked mention — outreach opportunity",
        "found_links": found_links,
        "emails_on_page": emails[:5],
        "contact_pages": list({c["url"]: c for c in contact_pages}.values())[:5],
    }, indent=2)


@mcp.tool()
def extract_contact_info(url: str) -> str:
    """
    Extract contact information from a page for outreach.

    Returns emails, social profiles, contact page links, and
    site title/description to help personalize your outreach email.

    Args:
        url: Page URL to extract contact info from
    """
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except Exception as e:
        return json.dumps({"error": str(e)})

    soup = BeautifulSoup(resp.text, "lxml")

    emails = list(set(re.findall(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resp.text
    )))
    emails = [e for e in emails if not any(
        ext in e for ext in [".png", ".jpg", ".svg", ".gif", ".css", ".js"]
    )]

    social = {}
    patterns = {
        "twitter": r"twitter\.com/([A-Za-z0-9_]{1,15})",
        "linkedin": r"linkedin\.com/(?:in|company)/([A-Za-z0-9_-]+)",
    }
    for platform, pattern in patterns.items():
        match = re.search(pattern, resp.text)
        if match:
            social[platform] = f"https://{match.group(0)}"

    contact_links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"].lower()
        if any(w in text or w in href for w in ["contact", "about", "write for us", "contribute", "advertise", "pitch"]):
            full = a["href"] if a["href"].startswith("http") else urljoin(url, a["href"])
            if full not in seen:
                seen.add(full)
                contact_links.append({"text": a.get_text(strip=True), "url": full})

    title = soup.find("title")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_author = soup.find("meta", attrs={"name": "author"})

    return json.dumps({
        "url": url,
        "site_title": title.get_text(strip=True) if title else "",
        "site_description": meta_desc["content"] if meta_desc and meta_desc.get("content") else "",
        "author": meta_author["content"] if meta_author and meta_author.get("content") else "",
        "emails": emails[:10],
        "social_profiles": social,
        "contact_pages": contact_links[:5],
    }, indent=2)


@mcp.tool()
def check_page_history(url: str) -> str:
    """
    Check the Wayback Machine archive history for a URL.

    Useful for:
    - Verifying a page that linked to you in the past still exists
    - Checking if a prospect's resource page has been stable over time
    - Finding broken/redirected pages for broken-link building

    Args:
        url: The URL to check history for
    """
    cdx_url = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": url,
        "output": "json",
        "limit": 10,
        "fl": "timestamp,statuscode,mimetype",
        "collapse": "timestamp:6",  # one snapshot per month
    }
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.get(cdx_url, params=params)
            data = resp.json()
    except Exception as e:
        return json.dumps({"error": str(e)})

    if not data or len(data) < 2:
        return json.dumps({
            "url": url,
            "archived": False,
            "message": "No Wayback Machine snapshots found for this URL.",
        })

    headers_row = data[0]
    snapshots = [dict(zip(headers_row, row)) for row in data[1:]]
    latest = snapshots[-1] if snapshots else {}
    latest_snapshot_url = (
        f"https://web.archive.org/web/{latest.get('timestamp', '')}/{url}"
        if latest else ""
    )

    return json.dumps({
        "url": url,
        "archived": True,
        "snapshot_count": len(snapshots),
        "latest_snapshot": latest_snapshot_url,
        "latest_status_code": latest.get("statuscode", ""),
        "history": snapshots,
    }, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
