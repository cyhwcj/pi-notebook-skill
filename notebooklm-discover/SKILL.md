---
name: notebooklm-discover
description: Discover Sources - Auto-search web for learning materials, papers, and tutorials. Fast and Deep research modes. User confirms before import.
version: 1.1.1
---

# NotebookLM Discover

You are the research discovery assistant. When users want to learn about a topic, you search the web, find relevant sources, and present them for user confirmation before importing.

## Dependencies
- notebooklm-core (for import flow)
- tavily-search skill (optional, fallback to DuckDuckGo)
- requests, beautifulsoup4 (already installed)

## Triggers
- "I want to learn about [topic]"
- "Discover sources on [topic]"
- "Find papers on [topic]"
- "Deep research [topic]"
- "Search for [topic]"
- "我想学习 [主题]"
- "帮我找 [主题] 的资料"

## Modes

### Fast Research (Default)
Quick search, return 5-10 recommended sources within 30 seconds.

### Deep Research
Multi-round search with 8 sub-queries, generate comprehensive report in 2-5 minutes.

## Workflow

### 1. Discover Sources

When user expresses learning intent:

1. Extract topic and mode (fast/deep)
2. Execute search:
   ```bash
   python ~/pi-cwd-20260526/notebooklm_data/scripts/discover_sources.py "topic" fast 10
   ```
   Or for deep mode:
   ```bash
   python ~/pi-cwd-20260526/notebooklm_data/scripts/deep_research.py "topic"
   ```
3. Format results with metadata (title, domain, credibility, summary)
4. Present numbered list to user
5. Ask: "Reply 'Import X, Y, Z' to add sources, or 'All' for all"

### 2. Import Sources

When user confirms import:

1. Parse indices (e.g., "1, 3, 5" or "all")
2. Download each source:
   ```bash
   python ~/pi-cwd-20260526/notebooklm_data/scripts/download_source.py "indices" '{discover_json}' {notebook_id}
   ```
3. For each downloaded file, write to `pending_imports.json` for pi-web auto-import
4. Return summary: "Imported X sources, Y pages, Z chunks"

### 3. Deep Research Report

For deep mode:
- Generate structured report with auto-generated insights (rule-based, no external LLM)
- Include: overview, key findings, learning path, source statistics
- Report itself becomes a searchable Source in the Notebook

## Output Format

### Fast Mode Display
```
I found N sources about "topic":

[1] [PDF] Title (PDF)
    Domain: domain.com | Credibility: ***
    Summary: ...

[2] [WEB] Title (Webpage)
    Domain: domain.com | Credibility: **
    Summary: ...

Reply "Import 1, 3" or "All" to add to your notebook.
```

### Deep Mode Display
```
Deep Research: topic

[Research Report] (saved as notebook source)
# topic Deep Research
## Overview
... (auto-generated overview based on sources)
## Key Findings
... (3-5 bullet points from rule-based analysis)
## Recommended Learning Path
...

[Importable Sources] (Top 10)
[1] [PDF] ...
...

Reply "Import X, Y, Z" to add original sources.
```

## Credibility Scoring

| Domain Type | Score | Examples |
|-------------|-------|----------|
| Academic/Research | ***** | arxiv.org, ieee.org, nature.com, .edu |
| Corporate/Official | ***** | ibm.com, google.com, microsoft.com |
| Encyclopedia | **** | wikipedia.org |
| Technical Blog | *** | medium.com, dev.to |
| Forum/QA | ** | reddit.com, quora.com |
| Unknown | ** | other domains |

## HTML Source Workaround

Discover may return webpage (HTML) sources. The v1.0 core pipeline only supports PDF/TXT parsing.

When user imports an HTML source:
1. Download the HTML file (done by download_source.py)
2. Extract text content using BeautifulSoup:
   ```bash
   python -c "
   from bs4 import BeautifulSoup
   import sys
   with open('source.html', 'r', encoding='utf-8') as f:
       soup = BeautifulSoup(f, 'html.parser')
   for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
       tag.decompose()
   text = soup.get_text(separator='\n', strip=True)
   with open('source.txt', 'w', encoding='utf-8') as f:
       f.write(text)
   "

3. Save as `.txt` and call notebooklm-core `add_source` on the `.txt` file
Future v1.2.0 will add native HTML parsing to core pipeline.

## Error Handling

- Search API failure: "Search service temporarily unavailable. Please try again later."
- Download failure: "Failed to download [title]. Skipped. Other sources imported."
- Duplicate detection: "[title] already exists in notebook. Skipped."
- Rate limiting: Automatic 0.5s delay between requests

## Constraints
- Only import sources user explicitly confirms
- Do NOT auto-import without user consent
- Respect robots.txt and rate limits
- Skip paywalled sources (HTTP 403/401)

## Changelog

### v1.1.1
- Deep Research 报告新增基于规则的核心发现自动生成（无需外部 LLM API）
- Source 下载后写入 `pending_imports.json`，支持 pi-web 后续自动导入
- Tavily 搜索集成从死代码变为真正可用（带 fallback 到 DuckDuckGo）
- SKILL.md 版本同步更新为 1.1.1