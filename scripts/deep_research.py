#!/usr/bin/env python3
"""Deep Research: Multi-round search with synthesized report."""
import sys
import json
import os
import time
import re
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from discover_sources import search_tavily, format_results

# Chinese and English stopwords for keyword extraction
STOPWORDS = {
    # Chinese common stopwords
    '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
    '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
    '自己', '这', '那', '里', '个', '来', '为', '与', '但', '或', '这个', '什么',
    '如何', '为什么', '怎么', '哪', '如何', '可以', '能', '用', '让', '把', '被',
    # English common stopwords
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
    'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have',
    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its',
    'which', 'what', 'who', 'whom', 'how', 'why', 'when', 'where'
}

def extract_keywords(summaries, top_n=10):
    """Extract high-frequency keywords from summaries (Chinese/English)."""
    if not summaries:
        return []

    # Combine all text and split into words
    all_words = []
    for summary in summaries:
        if not summary:
            continue
        # Extract Chinese characters and English words
        chinese_words = re.findall(r'[一-鿿]+', str(summary))
        english_words = re.findall(r'[a-zA-Z]+', str(summary))

        # Add Chinese words (keep as-is, they are usually meaningful)
        all_words.extend(chinese_words)

        # Add lowercase English words
        all_words.extend([w.lower() for w in english_words if len(w) > 2])

    # Filter out stopwords
    filtered = [w for w in all_words if w not in STOPWORDS and len(w) > 1]

    # Count frequency and get top N
    counter = Counter(filtered)
    return [word for word, count in counter.most_common(top_n)]

def generate_insights(sources, topic):
    """Generate core insights from sources without external LLM API."""
    if not sources:
        return {
            "overview": f"未找到关于「{topic}」的相关来源，请尝试更换关键词后重新搜索。",
            "core_findings": [],
            "type_distribution": {},
            "credibility_distribution": {}
        }

    # Group by credibility
    credibility_groups = {5: [], 4: [], 3: [], 2: [], 1: []}
    for s in sources:
        cred = s.get("credibility", 3)
        if cred > 5:
            cred = 5
        elif cred < 1:
            cred = 1
        credibility_groups[cred].append(s)

    # Type distribution
    type_dist = {"pdf": 0, "webpage": 0, "video": 0}
    for s in sources:
        t = s.get("type", "webpage")
        type_dist[t] = type_dist.get(t, 0) + 1

    # Extract keywords from top sources
    top_sources = sorted(sources, key=lambda x: x.get("credibility", 0), reverse=True)[:10]
    summaries = [s.get("summary", "") for s in top_sources]
    keywords = extract_keywords(summaries, top_n=8)

    # Generate overview (2-3 sentences)
    total = len(sources)
    high_cred = len(credibility_groups[5]) + len(credibility_groups[4])
    pdf_count = type_dist.get("pdf", 0)

    if high_cred > total * 0.5:
        overview = f"关于「{topic}」的调研显示，该领域有较高比例的权威学术资源（{high_cred}个高可信度来源），适合深入学习。"
    elif high_cred > total * 0.3:
        overview = f"关于「{topic}」的调研显示，资源类型多样（{total}个来源），包含{pdf_count}个PDF/论文类资料，建议优先阅读高可信度内容。"
    else:
        overview = f"关于「{topic}」的调研共找到{total}个相关来源，建议通过筛选可信度较高的资源开始学习。"

    # Generate core findings (3-5 bullet points)
    core_findings = []

    # Finding 1: Based on high credibility sources
    if credibility_groups[5]:
        top3 = credibility_groups[5][:3]
        titles = "、".join([s.get("title", "")[:20] for s in top3])
        core_findings.append(f"该领域权威资源包括：{titles}等高可信度来源。")

    # Finding 2: Based on keywords
    if keywords:
        core_findings.append(f"核心主题涵盖：{', '.join(keywords[:5])}等领域重点概念。")

    # Finding 3: Based on type distribution
    if pdf_count > 0:
        core_findings.append(f"发现{pdf_count}个学术论文类资源，建议作为系统学习的核心材料。")

    # Finding 4: Based on type distribution for videos
    video_count = type_dist.get("video", 0)
    if video_count > 0:
        core_findings.append(f"包含{video_count}个视频教程，适合入门阶段直观学习。")

    # Finding 5: Based on learning path observation
    web_count = type_dist.get("webpage", 0)
    if web_count > total * 0.5:
        core_findings.append(f"网络资源丰富（{web_count}个网页），适合了解最新进展和实践案例。")

    return {
        "overview": overview,
        "core_findings": core_findings[:5],  # Max 5 findings
        "type_distribution": type_dist,
        "credibility_distribution": {
            "5星": len(credibility_groups[5]),
            "4星": len(credibility_groups[4]),
            "3星及以下": len(credibility_groups[3]) + len(credibility_groups[2]) + len(credibility_groups[1])
        },
        "top_keywords": keywords
    }

def generate_sub_queries(topic):
    """Generate 5-10 sub-queries for comprehensive research."""
    templates = [
        "{topic} 入门教程",
        "{topic} 基础概念",
        "{topic} 最新进展",
        "{topic} 应用案例",
        "{topic} 经典论文",
        "{topic} 学习路径",
        "{topic} vs 传统方法",
        "{topic} 工具推荐"
    ]

    sub_queries = [t.format(topic=topic) for t in templates]
    return sub_queries[:8]

def deep_research(topic, max_per_query=5):
    """Execute deep research on topic."""
    print(f"Starting deep research on: {topic}", file=sys.stderr)

    sub_queries = generate_sub_queries(topic)
    print(f"Sub-queries: {sub_queries}", file=sys.stderr)

    all_results = []
    for i, q in enumerate(sub_queries):
        print(f"Searching ({i+1}/{len(sub_queries)}): {q}", file=sys.stderr)
        results = search_tavily(q, max_per_query)
        all_results.extend(results)
        time.sleep(0.5)

    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)

    unique_results.sort(key=lambda x: x.get("credibility", 0), reverse=True)

    # Generate insights
    insights = generate_insights(unique_results, topic)

    # Build core findings bullet points
    findings_text = ""
    if insights["core_findings"]:
        for finding in insights["core_findings"]:
            findings_text += f"- {finding}\n"
    else:
        findings_text = insights["overview"]

    report = f"""# {topic} 深度调研报告

## 调研概述
{insights["overview"]}

## 核心发现
{findings_text}## 推荐学习路径
1. 入门：选择可信度 5 星的教材或教程
2. 进阶：阅读经典论文
3. 实践：参考应用案例和工具推荐

## 来源统计
- 总计来源: {len(unique_results)}
- 高可信度(5星): {insights["credibility_distribution"].get("5星", 0)}
- 中等可信度(4星): {insights["credibility_distribution"].get("4星", 0)}
- 一般可信度(3星及以下): {insights["credibility_distribution"].get("3星及以下", 0)}
- PDF资源: {insights["type_distribution"].get("pdf", 0)}
- 网页资源: {insights["type_distribution"].get("webpage", 0)}
- 视频资源: {insights["type_distribution"].get("video", 0)}

## 关键词
{', '.join(insights.get("top_keywords", []))}

## 全部来源列表
"""

    for i, r in enumerate(unique_results[:30], 1):
        report += f"\n[{i}] {r.get('title', 'Untitled')}\n"
        report += f"    来源: {r.get('domain', 'unknown')} | 可信度: {'*' * r.get('credibility', 3)}\n"
        report += f"    URL: {r.get('url', 'N/A')}\n"
        report += f"    摘要: {r.get('summary', 'N/A')[:100]}...\n"

    return {
        "topic": topic,
        "mode": "deep",
        "total_sources": len(unique_results),
        "sub_queries": sub_queries,
        "report": report,
        "insights": insights,
        "top_sources": format_results(unique_results[:10], topic)["sources"]
    }

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    topic = sys.argv[1] if len(sys.argv) > 1 else "machine learning"
    result = deep_research(topic)
    print(json.dumps(result, ensure_ascii=False, indent=2))