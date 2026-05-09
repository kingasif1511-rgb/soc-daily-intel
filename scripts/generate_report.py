"""
Report Generator for SOC Daily Intelligence Feed.
Takes fetched articles and generates a formatted markdown report.
"""

import os
from datetime import datetime, timezone
from utils import (
    get_priority_emoji,
    get_category_emoji,
    classify_article,
    generate_threat_score,
    truncate_text,
    format_date
)


def generate_daily_report(articles: list, sources_analyzed: int) -> str:
    """
    Generate a complete daily SOC intelligence report in markdown format.
    
    Args:
        articles: List of article dicts with keys:
                  title, link, summary, source, published, priority, category
        sources_analyzed: Number of RSS sources that were successfully parsed
    
    Returns:
        Formatted markdown string
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    # Classify and score all articles
    for article in articles:
        article["soc_category"] = classify_article(
            article.get("title", ""),
            article.get("summary", "")
        )
        article["threat_score"] = generate_threat_score(
            article.get("title", ""),
            article.get("summary", ""),
            article.get("priority", "medium")
        )

    # Sort by threat score (highest first)
    articles.sort(key=lambda x: x.get("threat_score", 0), reverse=True)

    # Count by priority
    critical_count = sum(1 for a in articles if a.get("priority") == "critical")
    high_count = sum(1 for a in articles if a.get("priority") == "high")
    medium_count = sum(1 for a in articles if a.get("priority") == "medium")

    # Group articles by SOC category
    categorized = {}
    for article in articles:
        cat = article.get("soc_category", "General Security News")
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(article)

    # Build the report
    lines = []

    # Header
    lines.append(f"# 🛡️ SOC Daily Intelligence Report — {date_str}")
    lines.append("")
    lines.append(f"> Auto-generated SOC analysis report | Sources: {sources_analyzed} feeds | Articles: {len(articles)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Threat Summary Table
    lines.append("## 📊 Daily Threat Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| 📰 Total Articles | **{len(articles)}** |")
    lines.append(f"| 🔴 Critical Priority | **{critical_count}** |")
    lines.append(f"| 🟠 High Priority | **{high_count}** |")
    lines.append(f"| 🟡 Medium Priority | **{medium_count}** |")
    lines.append(f"| 📡 Sources Analyzed | **{sources_analyzed}** |")
    lines.append("")

    # Top Threats (top 5 by score)
    if articles:
        lines.append("---")
        lines.append("")
        lines.append("## 🚨 Top Threats Today")
        lines.append("")
        top_articles = articles[:5]
        for i, article in enumerate(top_articles, 1):
            emoji = get_priority_emoji(article.get("priority", "medium"))
            score = article.get("threat_score", 0)
            lines.append(f"### {i}. {emoji} {article.get('title', 'Untitled')}")
            lines.append(f"- **Source**: {article.get('source', 'Unknown')}")
            lines.append(f"- **Category**: {article.get('soc_category', 'N/A')}")
            lines.append(f"- **Threat Score**: `{score}/100`")
            lines.append(f"- **Published**: {article.get('published', 'Unknown')}")
            summary = truncate_text(article.get("summary", ""), 400)
            if summary:
                lines.append(f"- **Summary**: {summary}")
            lines.append(f"- 🔗 [Read Full Article]({article.get('link', '#')})")
            lines.append("")

    # Categorized Articles
    lines.append("---")
    lines.append("")
    lines.append("## 📂 Categorized Intelligence")
    lines.append("")

    # Sort categories by number of articles (descending)
    sorted_categories = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)

    for category, cat_articles in sorted_categories:
        cat_emoji = get_category_emoji(category)
        lines.append(f"### {cat_emoji} {category} ({len(cat_articles)} articles)")
        lines.append("")

        for article in cat_articles:
            priority_emoji = get_priority_emoji(article.get("priority", "medium"))
            score = article.get("threat_score", 0)
            title = article.get("title", "Untitled")
            link = article.get("link", "#")
            source = article.get("source", "Unknown")
            published = article.get("published", "Unknown")
            summary = truncate_text(article.get("summary", ""), 250)

            lines.append(f"<details>")
            lines.append(f"<summary>{priority_emoji} <b>{title}</b> — <i>{source}</i> (Score: {score})</summary>")
            lines.append(f"")
            lines.append(f"- **Published**: {published}")
            lines.append(f"- **Priority**: {article.get('priority', 'medium').upper()}")
            if summary:
                lines.append(f"- **Summary**: {summary}")
            lines.append(f"- 🔗 [Read More]({link})")
            lines.append(f"")
            lines.append(f"</details>")
            lines.append(f"")

        lines.append("")

    # Source Breakdown
    source_counts = {}
    for article in articles:
        src = article.get("source", "Unknown")
        source_counts[src] = source_counts.get(src, 0) + 1

    lines.append("---")
    lines.append("")
    lines.append("## 📡 Source Breakdown")
    lines.append("")
    lines.append("| Source | Articles |")
    lines.append("|--------|----------|")
    for src, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {src} | {count} |")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("## 📝 Report Metadata")
    lines.append("")
    lines.append(f"- **Generated**: {timestamp}")
    lines.append(f"- **Report Date**: {date_str}")
    lines.append(f"- **Total Sources**: {sources_analyzed}")
    lines.append(f"- **Total Articles**: {len(articles)}")
    lines.append(f"- **Top Category**: {sorted_categories[0][0] if sorted_categories else 'N/A'}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 🤖 *This report was automatically generated by [SOC Daily Intel](https://github.com/YOUR_USERNAME/soc-daily-intel) — Keeping your GitHub green while staying informed on cybersecurity threats.*")
    lines.append("")

    return "\n".join(lines)


def generate_index_entry(date_str: str, article_count: int, top_category: str) -> str:
    """Generate a single-line entry for the monthly index."""
    return f"| {date_str} | {article_count} | {top_category} | [📄 View Report](reports/{date_str[:4]}/{date_str[5:7]}/{date_str}.md) |"
