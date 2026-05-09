# 🛡️ SOC Daily Intelligence Feed

[![Daily SOC Intel Update](https://github.com/YOUR_USERNAME/soc-daily-intel/actions/workflows/daily-update.yml/badge.svg)](https://github.com/YOUR_USERNAME/soc-daily-intel/actions/workflows/daily-update.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/soc-daily-intel)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/YOUR_USERNAME/soc-daily-intel)

> **Automated daily Security Operations Center (SOC) intelligence reports** — curated from top cybersecurity news sources, threat intelligence feeds, and vulnerability databases.

---

## 📋 What is This?

This repository automatically fetches, processes, and commits **daily SOC analysis reports** from leading cybersecurity news sources. Each day, a new markdown report is generated containing:

- 🔴 **Critical Vulnerabilities & CVEs** — Latest vulnerability disclosures
- 🔵 **Threat Intelligence** — Emerging threat actors and campaigns
- 🟡 **Incident Reports** — Notable security breaches and incidents
- 🟢 **SOC Best Practices** — Tools, techniques, and defensive strategies
- 🟣 **Malware Analysis** — New malware families and indicators of compromise

## 📰 News Sources

| Source | Category | Feed |
|--------|----------|------|
| The Hacker News | General Cybersecurity | RSS |
| CISA Alerts | Government Advisories | RSS |
| Krebs on Security | Investigative Security | RSS |
| BleepingComputer | Malware & Vulnerabilities | RSS |
| Dark Reading | Enterprise Security | RSS |
| SecurityWeek | Industry News | RSS |
| SANS ISC | Threat Analysis | RSS |
| Threatpost | Threat Intelligence | RSS |
| Naked Security (Sophos) | Security Research | RSS |
| NIST NVD | CVE Database | API |

## 📂 Repository Structure

```
soc-daily-intel/
├── .github/
│   └── workflows/
│       └── daily-update.yml          # GitHub Actions automation
├── scripts/
│   ├── fetch_soc_news.py             # Main news fetcher script
│   ├── generate_report.py            # Report generator
│   └── utils.py                      # Utility functions
├── reports/
│   └── YYYY/
│       └── MM/
│           └── YYYY-MM-DD.md         # Daily reports
├── data/
│   └── sources.json                  # RSS feed sources configuration
├── templates/
│   └── daily_report.md               # Report template
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🚀 Quick Setup

### 1. Fork This Repository
Click the **Fork** button at the top-right of this page.

### 2. Enable GitHub Actions
Go to your fork → **Settings** → **Actions** → **General** → Select **"Allow all actions"**

### 3. Set Permissions
Go to **Settings** → **Actions** → **General** → **Workflow permissions** → Select **"Read and write permissions"**

### 4. Update Badge URLs
In this README, replace `YOUR_USERNAME` with your GitHub username.

### 5. That's It! 🎉
The workflow runs automatically every day at **06:00 UTC**. You can also trigger it manually from the **Actions** tab.

## 🔧 Manual Run

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/soc-daily-intel.git
cd soc-daily-intel

# Install dependencies
pip install -r requirements.txt

# Run the daily update
python scripts/fetch_soc_news.py
```

## ⚙️ Configuration

### Change Update Time
Edit `.github/workflows/daily-update.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '0 6 * * *'  # Runs at 06:00 UTC daily
```

### Add/Remove News Sources
Edit `data/sources.json` to add or remove RSS feeds.

## 📊 Contribution Streak

This repository is designed to maintain your GitHub contribution graph by making meaningful daily commits with real cybersecurity intelligence data. Each commit contains:

- A new daily report with curated SOC news
- Updated threat statistics
- Fresh vulnerability data

> ⚠️ **Note**: GitHub counts commits to the default branch for the contribution graph. Make sure the workflow has write permissions.

## 📈 Stats

- **Started**: May 2026
- **Goal**: 5+ years of daily SOC intelligence
- **Total Reports**: Growing daily!

## 🤝 Contributing

Feel free to:
- Add new intelligence sources
- Improve report formatting
- Suggest new analysis categories
- Report issues with feed parsing

## 📜 License

This project is licensed under the MIT License. The news content belongs to their respective sources and is used under fair use for educational purposes.

---

<p align="center">
  <b>🔒 Stay informed. Stay secure. Stay green. 🟢</b>
</p>
