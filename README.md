# backlink-mcp

**[Full docs & install guide → sellonllm.com/backlink-mcp.html](https://www.sellonllm.com/backlink-mcp.html)**

> Automate backlink research, unlinked mention hunting, and outreach prep inside your AI assistant. Free, no API keys required.

Connect to **Claude**, **Cursor**, or any MCP-compatible AI assistant and let it find backlink opportunities, discover unlinked mentions, research prospects, and extract contact info for outreach — all for free.

Part of the **[SellOnLLM SEO MCP suite](https://www.sellonllm.com)** — a hub of free MCP servers for SEO and AI visibility.

---

## Why this exists

Tools like Ahrefs and Moz cost hundreds of dollars a month. This MCP gives you backlink research capabilities directly inside your AI assistant at zero cost, using:

- **DuckDuckGo** — mention discovery and prospect finding
- **Wayback Machine CDX API** — historical link data
- **httpx + BeautifulSoup** — page scraping and link verification

---

## Tools

| Tool | Description |
|---|---|
| `find_mentions` | Find all pages mentioning your domain (linked or unlinked) |
| `find_prospects` | Discover guest post, resource page, and roundup opportunities by niche |
| `find_competitor_link_sources` | Find pages linking to a competitor — prime outreach targets |
| `verify_page_links` | Scrape a URL to check if it links to you and extract contact info |
| `extract_contact_info` | Pull emails, social handles, and contact pages from any site |
| `check_page_history` | Check Wayback Machine history — verify a page still exists |

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/vipul510-web/mcp-backlink-for-seo.git
cd mcp-backlink-for-seo
python3 -m venv .venv
.venv/bin/pip install mcp duckduckgo-search httpx beautifulsoup4 lxml
```

### 2. Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "backlink-mcp": {
      "command": "/absolute/path/to/backlink-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/backlink-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop. The backlink tools will appear automatically.

### 3. Connect to Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

```json
{
  "mcpServers": {
    "backlink-mcp": {
      "command": "/absolute/path/to/backlink-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/backlink-mcp/server.py"]
    }
  }
}
```

### 4. Connect to any MCP-compatible client

```bash
.venv/bin/python server.py
```

The server communicates over stdio, compatible with any MCP client.

---

## Usage examples

Once connected, just talk to your AI assistant:

**Find unlinked mentions (outreach opportunities):**
```
Find unlinked mentions of mybrand.com
```

**Discover guest post opportunities:**
```
Find guest post opportunities in the personal finance niche
```

**Research a competitor's backlinks:**
```
Who links to competitor.com? Find me 20 results.
```

**Verify and enrich a prospect:**
```
Check if techblog.com/article links to mybrand.com and find their contact email
```

**Full link building workflow:**
```
1. Find prospects in the SaaS marketing niche
2. Verify which ones don't already link to mysaas.com
3. Extract contact info for the top 5
4. Draft an outreach email for each
```

---

## Typical workflow

```
find_prospects / find_mentions / find_competitor_link_sources
                    ↓
              verify_page_links
          (linked or unlinked? contact info?)
                    ↓
           extract_contact_info
              (email, socials)
                    ↓
          outreach via Gmail MCP
```

---

## Requirements

- Python 3.10+
- No API keys needed
- No paid subscriptions

---

## Limitations

- DuckDuckGo returns a sample of results, not a complete link graph
- Rate limiting: built-in 1.5s delay between searches to avoid blocks
- Common Crawl graph data (full inbound link index) is not yet integrated — contributions welcome

---

## Contributing

PRs welcome. High-impact areas:

- Common Crawl graph API integration for true inbound link discovery
- Broken link detection (find dead pages on prospect sites)
- Bulk processing (run across a list of URLs)
- Output to CSV / Google Sheets

---

## Part of SellOnLLM

This MCP is part of the [SellOnLLM](https://www.sellonllm.com) SEO MCP suite — free, open-source MCP servers for SEO and AI visibility built for Claude and Cursor.

- [Backlink MCP](https://www.sellonllm.com/backlink-mcp.html) — this tool
- [GA4 + Search Console MCP](https://www.sellonllm.com) — query your traffic and rankings from your AI assistant
- [AI Visibility MCP](https://www.sellonllm.com) — check if your site is cited by AI tools like Perplexity

---

## License

MIT
