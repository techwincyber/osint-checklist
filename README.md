# OSINT Engagement Checklist - Copyright © Techwin 2026

A professional desktop GUI application for managing authorised OSINT engagements.
Built in Python with a dark terminal-inspired theme.

> ⚠️ **For authorised engagements only.** Always obtain written permission before conducting any reconnaissance activity.

---

## Features

- ✅ 6-phase checklist covering the full OSINT engagement lifecycle
- 💾 Save / load sessions as JSON files on your local machine
- 📝 Per-item finding notes with inline preview
- 📊 Live progress tracking — overall %, phase stats, completion ring
- 🔍 Filter by passive / active / incomplete / complete
- 📄 One-click Markdown report export (paste into GitHub or a Word doc)
- 🔁 Auto-saves when you close — reopens your last session automatically
- 🌑 Fully offline — nothing leaves your machine

## Phases Covered

| Phase | Description |
|-------|-------------|
| 0 — Scope & Authorisation | Legal groundwork, written permission, VM setup |
| 1 — Passive Reconnaissance | WHOIS, DNS, subdomains, dorking, breach data |
| 2 — Technology Footprint | CMS, cloud buckets, TLS, email security |
| 3 — People & Social Footprint | LinkedIn, GitHub, job postings, dark web |
| 4 — Active Reconnaissance | Port scans, brute-force, spidering, screenshots |
| 5 — Analysis & Reporting | Evidence, executive summary, secure delivery |

## Requirements

- Python 3.8+
- `customtkinter` library

## Installation

```bash
# 1. Clone or download this repo
git clone https://github.com/techwincyber/osint-checklist

# 2. Install the one dependency
pip install customtkinter

# 3. Run
python osint_checklist.py
```

On Windows you can also double-click `run.bat`.

## Usage

1. Enter your target in the **TARGET** field at the top of the sidebar
2. Work through each phase, ticking items as you complete them
3. Click 📝 on any item to add finding notes
4. Use **Save As…** to create a named JSON file for the engagement
5. Use **Export MD** to generate a Markdown report at any point

### File storage

Sessions are saved as `.json` files in an `osint_saves/` folder next to the script.
The app remembers your last session and reopens it automatically.

## Legal Disclaimer

**This tool is provided by Techwin strictly for lawful, authorised security assessment/research purposes only.**

By downloading, installing, or using this tool in any capacity, you agree to the following terms:

- You **must** hold explicit, written authorisation from the asset owner before conducting any reconnaissance activity. Using this tool without such authorisation is illegal.
- This tool is designed solely to assist security professionals in **authorised** engagements. It is **not** designed, intended, or licensed for offensive, malicious, or unauthorised use of any kind.
- **Techwin accepts absolutely no responsibility or liability** for any misuse, damage, legal consequences, or harm — direct or indirect — arising from the use or misuse of this tool by any individual or organisation.
- Unauthorised reconnaissance, data collection, or intrusion activity may constitute a criminal offence under the Computer Misuse Act 1990 (UK), the Computer Fraud and Abuse Act (CFAA, US), the General Data Protection Regulation (GDPR), and equivalent legislation in your jurisdiction. Prosecution may result in significant fines and/or imprisonment.
- Techwin makes no warranties, express or implied, regarding the fitness, accuracy, or completeness of this tool for any particular purpose.

**If you are not authorised — do not use this tool. Ignorance of the law is not a defence.**
