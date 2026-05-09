#!/usr/bin/env python3
"""
SOC Daily Intelligence Feed — Main News Fetcher
Fetches cybersecurity news from multiple RSS feeds, processes them,
and generates a daily markdown report for GitHub contribution streak.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from dateutil import parser as date_parser

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    sanitize_html,
    truncate_text,
    generate_article_id,
    get_today_str,
    get_year_month,
    format_date
)
from generate_report import generate_daily_report

# ----- Configuration -----

# Paths (relative to repo root)
REPO_ROOT = Path(__file__).parent.parent
SOURCES_FILE = REPO_ROOT / "data" / "sources.json"
REPORTS_DIR = REPO_ROOT / "reports"
LOG_FILE = REPO_ROOT / "scripts" / "fetch.log"

# Request settings
REQUEST_TIMEOUT = 15  # seconds
REQUEST_HEADERS = {
    "User-Agent": "SOC-Daily-Intel/1.0 (GitHub Action; Cybersecurity News Aggregator)"
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger("soc-intel")


def load_sources() -> dict:
    """Load RSS feed sources from the JSON configuration file."""
    try:
        with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data.get('feeds', []))} feed sources")
        return data
    except FileNotFoundError:
        logger.error(f"Sources file not found: {SOURCES_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sources file: {e}")
        sys.exit(1)


def fetch_feed(feed_config: dict) -> list:
    """
    Fetch and parse a single RSS feed.
    
    Args:
        feed_config: Dict with keys: name, url, category, priority, enabled
    
    Returns:
        List of article dicts
    """
    name = feed_config.get("name", "Unknown")
    url = feed_config.get("url", "")
    priority = feed_config.get("priority", "medium")
    category = feed_config.get("category", "General")

    if not feed_config.get("enabled", True):
        logger.info(f"Skipping disabled feed: {name}")
        return []

    logger.info(f"Fetching: {name} ({url})")
    articles = []

    try:
        # Fetch the feed with a timeout
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        # Parse the feed
        feed = feedparser.parse(response.content)

        if feed.bozo and not feed.entries:
            logger.warning(f"Feed parse error for {name}: {feed.bozo_exception}")
            return []

        # Process entries
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        for entry in feed.entries:
            try:
                # Parse publication date
                pub_date = None
                for date_field in ['published', 'updated', 'created']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        try:
                            pub_date = date_parser.parse(getattr(entry, date_field))
                            break
                        except (ValueError, TypeError):
                            continue

                # Filter: only include articles from last 48 hours
                if pub_date:
                    pub_date_aware = pub_date if pub_date.tzinfo else pub_date.replace(tzinfo=timezone.utc)
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
                    if pub_date_aware < cutoff:
                        continue

                # Extract title
                title = sanitize_html(getattr(entry, 'title', 'Untitled'))
                if not title:
                    continue

                # Extract link
                link = getattr(entry, 'link', '')

                # Extract summary
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = sanitize_html(entry.summary)
                elif hasattr(entry, 'description'):
                    summary = sanitize_html(entry.description)
                elif hasattr(entry, 'content') and entry.content:
                    summary = sanitize_html(entry.content[0].get('value', ''))
                summary = truncate_text(summary, 500)

                # Build article dict
                article = {
                    "id": generate_article_id(title, name),
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": name,
                    "category": category,
                    "priority": priority,
                    "published": format_date(pub_date, "%Y-%m-%d %H:%M UTC") if pub_date else "Unknown",
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                }
                articles.append(article)

            except Exception as e:
                logger.warning(f"Error processing entry from {name}: {e}")
                continue

        logger.info(f"  ✅ {name}: {len(articles)} articles found")

    except requests.exceptions.Timeout:
        logger.warning(f"  ⏱️ Timeout fetching {name}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"  ❌ Connection error for {name}")
    except requests.exceptions.HTTPError as e:
        logger.warning(f"  ❌ HTTP error for {name}: {e}")
    except Exception as e:
        logger.error(f"  ❌ Unexpected error fetching {name}: {e}")

    return articles


def deduplicate_articles(articles: list) -> list:
    """Remove duplicate articles based on their generated ID."""
    seen_ids = set()
    unique = []
    for article in articles:
        aid = article.get("id", "")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            unique.append(article)
    logger.info(f"Deduplication: {len(articles)} → {len(unique)} articles")
    return unique


def save_report(report_content: str, date_str: str) -> str:
    """Save the report to the appropriate directory structure."""
    year, month = date_str[:4], date_str[5:7]
    report_dir = REPORTS_DIR / year / month
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"{date_str}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"Report saved: {report_path}")
    return str(report_path)


def update_latest_symlink(date_str: str):
    """Update the LATEST.md file in the repo root to point to today's report."""
    year, month = date_str[:4], date_str[5:7]
    latest_path = REPO_ROOT / "LATEST.md"
    report_rel_path = f"reports/{year}/{month}/{date_str}.md"

    content = f"""# 🛡️ Latest SOC Intelligence Report

📅 **Date**: {date_str}

👉 **[View Today's Full Report]({report_rel_path})**

---

*This file is automatically updated daily. Check the [reports](reports/) directory for the full archive.*
"""
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info("Updated LATEST.md")


def update_stats_file(date_str: str, article_count: int, sources_count: int):
    """Update the cumulative stats JSON file."""
    stats_path = REPO_ROOT / "data" / "stats.json"

    # Load existing stats or create new
    if stats_path.exists():
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = {
            "first_report": date_str,
            "total_reports": 0,
            "total_articles_processed": 0,
            "daily_log": []
        }

    # Update stats
    stats["last_report"] = date_str
    stats["total_reports"] = stats.get("total_reports", 0) + 1
    stats["total_articles_processed"] = stats.get("total_articles_processed", 0) + article_count

    # Add daily entry (keep last 365 days)
    stats["daily_log"].append({
        "date": date_str,
        "articles": article_count,
        "sources": sources_count
    })
    stats["daily_log"] = stats["daily_log"][-365:]

    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Updated stats: {stats['total_reports']} total reports, {stats['total_articles_processed']} total articles")


def main():
    """Main execution flow."""
    logger.info("=" * 60)
    logger.info("🛡️  SOC Daily Intelligence Feed — Starting Update")
    logger.info("=" * 60)

    start_time = time.time()
    date_str = get_today_str()
    logger.info(f"📅 Report date: {date_str}")

    # Load sources
    sources_data = load_sources()
    feeds = sources_data.get("feeds", [])
    settings = sources_data.get("settings", {})
    max_per_source = settings.get("max_articles_per_source", 5)
    max_total = settings.get("max_total_articles", 40)

    # Fetch all feeds
    all_articles = []
    sources_ok = 0

    for feed_config in feeds:
        articles = fetch_feed(feed_config)
        if articles:
            sources_ok += 1
            # Limit per source
            all_articles.extend(articles[:max_per_source])
        # Small delay between requests to be polite
        time.sleep(1)

    logger.info(f"\n📊 Fetched {len(all_articles)} articles from {sources_ok}/{len(feeds)} sources")

    # Deduplicate
    all_articles = deduplicate_articles(all_articles)

    # Limit total articles
    if len(all_articles) > max_total:
        all_articles = all_articles[:max_total]
        logger.info(f"Trimmed to {max_total} articles (max_total setting)")

    # Handle case with no articles (still generate a report for the streak!)
    if not all_articles:
        logger.warning("⚠️ No articles fetched! Generating placeholder report for streak.")
        all_articles = [{
            "id": "placeholder",
            "title": "No New Articles Today",
            "link": "#",
            "summary": "No new cybersecurity articles were found in the configured feeds today. "
                       "This can happen due to network issues or feed downtime. "
                       "The next update will attempt to fetch fresh content.",
            "source": "System",
            "category": "Info",
            "priority": "low",
            "published": date_str,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }]

    # Generate the report
    logger.info("📝 Generating daily report...")
    report_content = generate_daily_report(all_articles, sources_ok)

    # Save the report
    report_path = save_report(report_content, date_str)

    # Update LATEST.md
    update_latest_symlink(date_str)

    # Update stats
    update_stats_file(date_str, len(all_articles), sources_ok)

    elapsed = time.time() - start_time
    logger.info(f"\n✅ Done! Report generated in {elapsed:.1f}s")
    logger.info(f"📄 Report: {report_path}")
    logger.info(f"📊 Articles: {len(all_articles)} | Sources: {sources_ok}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
