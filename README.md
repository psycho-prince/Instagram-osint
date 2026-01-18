---

<p align="center">
  <img src="https://raw.githubusercontent.com/blackeko/yesitsme/media/logo.png" alt="yesitsme logo" width="180">
</p>

<h2 align="center">INSTAGRAM-OSINT!</h2>

<p align="center">
  Advanced Instagram & Cross-Platform OSINT Framework  
  <br>
  <sub>Identity correlation · Username intelligence · Timeline analysis</sub>
</p>

---

## 💬 Description

**yesitsme** is an advanced **Open-Source Intelligence (OSINT) framework** designed to correlate Instagram identities with usernames, historical traces, and cross-platform signals.

Originally inspired by the concept of matching Instagram profiles via names, emails, and phone fragments, this project has evolved into a **modular, async OSINT pipeline** capable of:

- Resolving Instagram user IDs via authenticated sessions
- Extracting rich public profile metadata
- Tracking username variants & historical traces
- Performing cross-platform username correlation
- Conducting Twitter/X and Reddit deep OSINT
- Generating search-engine dorks for old usernames
- Inferring timeline consistency and behavioral signals
- Producing investigator-ready reports (JSON & Markdown)

The framework is **read-only**, **non-intrusive**, and intended for **lawful investigations, research, and education**.

---

## ⚙️ Features

- ✅ Instagram profile resolution via cookies
- 🔁 Username variant & similarity clustering
- 🧭 Timeline consistency analysis
- 🐦 Twitter/X deep OSINT  
  - Bio parsing  
  - URL extraction  
  - Historical snapshot via search engines  
  - Email pattern inference
- 👽 Reddit timeline & subreddit intelligence
- 🕸️ Leak signal detection (mentions only)
- 🔎 Automated Google & Bing dork generation
- 📊 Confidence scoring & risk grading
- 📁 Batch mode (multi-target investigations)
- 🧾 JSON & Markdown report export

---

## ⚙️ Installation

```bash
git clone https://github.com/psycho-prince/Instagram-osint.git
cd Instagram-osint
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

> Note: Python 3.10+ recommended




---

🍪 Instagram Authentication (Required)

This tool requires your own Instagram session cookies (sockpuppet recommended).

How to retrieve cookies:

1. Log in to Instagram in a browser


2. Open Developer Tools → Application → Cookies


3. Copy cookies into a JSON file (example below)



Example cookies.json:

[
  {
    "name": "sessionid",
    "value": "YOUR_SESSION_ID",
    "domain": ".instagram.com"
  }
]


---

🕹️ Usage

Single Target Investigation

python main.py \
  -u "__username__" \
  --cookies-file cookies.json \
  --debug \
  --json result.json \
  --md result.md

Batch Mode (Multiple Targets)

python main.py \
  -U usernames.txt \
  --cookies-file cookies.json \
  --json reports/

Where usernames.txt contains:

username1
username2
username3


---

📊 Output

Match Levels

NONE – No strong correlation

LOW – Weak or partial signals

MEDIUM – Cross-platform correlation

HIGH – Strong identity convergence


Risk Grades

LOW – Sparse or inconsistent data

MEDIUM – Partial behavioral alignment

HIGH – Strong multi-source correlation



---

🧾 Example Report Artifacts

result__username__.json → machine-readable

result__username__.md → investigator-ready


Includes:

Profile metadata

Username history & variants

Cross-platform presence

Timeline analysis

Leak signal references

Search engine dorks

Confidence & risk explanation



---

📝 Notes & Limitations

This tool does not brute-force, exploit, or bypass authentication

Emails and phone numbers are not hacked or recovered

“Email inference” is probabilistic, not verification

Effectiveness depends on public footprint & OPSEC hygiene



---

⚠️ Legal & Ethical Disclaimer

This project is intended strictly for educational purposes, authorized investigations, and lawful OSINT research.

You are solely responsible for complying with:

Local laws

Platform Terms of Service

Ethical investigation standards


Do not use this tool for harassment, stalking, or unauthorized surveillance.


---

🙏 Credits & Inspiration

Original concept & inspiration: blackeko / yesitsme

Toutatis OSINT methodology

Dumpor indexing insights

OSINT community research & best practices



---

<p align="center">
  <sub>Built with ❤️ by @rhyugen</sub>
</p>
```
---
