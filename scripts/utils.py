"""
Utility functions for the SOC Daily Intelligence Feed.
Handles text processing, sanitization, and helper operations.
"""

import re
import html
import hashlib
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def sanitize_html(raw_html: str) -> str:
    """Remove HTML tags and decode entities from a string."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = html.unescape(text)
    # Collapse multiple whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to a maximum length, adding ellipsis if needed."""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].rsplit(' ', 1)[0] + "..."


def generate_article_id(title: str, source: str) -> str:
    """Generate a unique hash ID for an article based on title and source."""
    raw = f"{title.lower().strip()}|{source.lower().strip()}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()[:12]


def get_priority_emoji(priority: str) -> str:
    """Return an emoji based on priority level."""
    emojis = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "info": "🔵"
    }
    return emojis.get(priority.lower(), "⚪")


def get_category_emoji(category: str) -> str:
    """Return an emoji based on news category."""
    cat = category.lower()
    if "vuln" in cat or "cve" in cat or "exploit" in cat:
        return "🔓"
    elif "malware" in cat:
        return "🦠"
    elif "threat" in cat:
        return "⚠️"
    elif "government" in cat or "advisory" in cat or "alert" in cat:
        return "🏛️"
    elif "incident" in cat or "breach" in cat:
        return "🚨"
    elif "research" in cat or "analysis" in cat:
        return "🔬"
    elif "enterprise" in cat or "industry" in cat:
        return "🏢"
    elif "investigat" in cat:
        return "🔍"
    else:
        return "📰"


def format_date(date_obj, fmt: str = "%Y-%m-%d %H:%M UTC") -> str:
    """Format a datetime object to a string."""
    if not date_obj:
        return "Unknown"
    if isinstance(date_obj, str):
        return date_obj
    try:
        return date_obj.strftime(fmt)
    except Exception:
        return str(date_obj)


def get_today_str() -> str:
    """Get today's date string in YYYY-MM-DD format (UTC)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_year_month() -> tuple:
    """Get current year and month as strings."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y"), now.strftime("%m")


def classify_article(title: str, summary: str) -> str:
    """Classify an article into a SOC-relevant category based on keywords."""
    text = f"{title} {summary}".lower()

    # Keyword-based classification
    categories = {
        "Vulnerability & CVE": [
            "cve-", "vulnerability", "patch", "zero-day", "0day",
            "exploit", "buffer overflow", "rce", "sql injection",
            "xss", "privilege escalation", "security update"
        ],
        "Malware & Ransomware": [
            "malware", "ransomware", "trojan", "botnet", "backdoor",
            "worm", "spyware", "adware", "rootkit", "keylogger",
            "infostealer", "loader", "cryptominer"
        ],
        "Threat Intelligence": [
            "apt", "threat actor", "campaign", "nation-state",
            "espionage", "threat group", "attack chain", "ttps",
            "mitre att&ck", "ioc", "indicator of compromise"
        ],
        "Data Breach & Incident": [
            "breach", "data leak", "exposed", "compromised",
            "incident", "attack", "hacked", "stolen data",
            "unauthorized access"
        ],
        "SOC & Defense": [
            "soc", "siem", "detection", "monitoring", "edr",
            "xdr", "incident response", "forensic", "threat hunting",
            "blue team", "security operations", "playbook"
        ],
        "Cloud & Infrastructure": [
            "cloud security", "aws", "azure", "gcp", "kubernetes",
            "container", "misconfiguration", "saas", "iaas"
        ],
        "Compliance & Policy": [
            "compliance", "regulation", "gdpr", "hipaa", "pci",
            "nist", "iso 27001", "framework", "audit", "policy"
        ]
    }

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "General Security News"


def generate_threat_score(title: str, summary: str, priority: str) -> int:
    """Generate a simple threat relevance score (0-100) for an article."""
    score = 0
    text = f"{title} {summary}".lower()

    # Priority base score
    priority_scores = {"critical": 40, "high": 30, "medium": 20, "low": 10}
    score += priority_scores.get(priority.lower(), 15)

    # Keyword boosters
    high_impact_keywords = [
        "zero-day", "0day", "critical", "actively exploited",
        "in the wild", "emergency", "severe", "rce",
        "remote code execution", "nation-state", "apt"
    ]
    medium_impact_keywords = [
        "vulnerability", "cve-", "ransomware", "breach",
        "malware", "exploit", "patch", "attack"
    ]

    for kw in high_impact_keywords:
        if kw in text:
            score += 8

    for kw in medium_impact_keywords:
        if kw in text:
            score += 4

    return min(score, 100)
