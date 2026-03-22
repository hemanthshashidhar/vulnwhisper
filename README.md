<div align="center">

# 🕵️ VulnWhisper

### AI-Powered Bug Bounty Recon Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/Powered%20by-OpenRouter-purple?style=flat-square)](https://openrouter.ai)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

> *Stop running tools manually. Let an AI agent think, act, and reason through your recon — the way an experienced hunter would.*

![VulnWhisper Demo](assets/demo.gif)

</div>

---

## 🧠 What is VulnWhisper?

VulnWhisper is a **ReAct-based AI agent** (Reason → Act → Observe → Repeat) that performs intelligent bug bounty reconnaissance on a target domain.

Unlike traditional recon pipelines that blindly run tools in sequence, VulnWhisper **thinks**. It decides what to check next based on what it observes — chasing interesting threads, trying bypasses when it hits walls, and building a mental model of the target just like an experienced hunter would.

**Give it a domain. Walk away. Come back to a full report.**

---

## ⚡ How It Works
```
vulnwhisper target.com
        │
        ▼
┌─────────────────────────────────────┐
│         AI ReAct Agent Loop         │
│                                     │
│  💭 THINK  →  What should I check?  │
│  ⚡ ACT    →  Run the right tool    │
│  📡 OBSERVE →  Parse the output     │
│  💭 THINK  →  What does this mean?  │
│  ⚡ ACT    →  Follow the thread     │
└─────────────────────────────────────┘
        │
        ▼
  📄 reports/target_timestamp.md
```

---

## 🛠️ Tool Arsenal

| Tool | What It Does |
|------|-------------|
| `dns_lookup` | DNS resolution + WHOIS enumeration |
| `subdomain_enum` | Passive subdomain discovery via subfinder |
| `curl_probe` | HTTP/HTTPS probing with custom headers |
| `ssl_inspect` | SSL certificate analysis + SAN extraction |
| `httpx_probe` | Bulk subdomain probing with tech detection |
| `path_fuzz` | Common path fuzzing (APIs, admin panels, configs) |
| `header_bypass` | 403 bypass attempts via header injection |
| `s3_check` | AWS S3 bucket misconfiguration detection |
| `graphql_introspect` | GraphQL schema introspection |
| `upload_probe` | Upload endpoint discovery and probing |

---

## 🎯 Two Modes

### 🤖 Autonomous Mode
```bash
python main.py target.com
```
Fully autonomous. The agent runs without interruption and saves a report when done. Best for experienced hunters who want results fast.

### 🧭 Guided Mode (Beginner Friendly)
```bash
python main.py target.com --guided
```
The agent explains its reasoning and asks for confirmation before each action. **Perfect for learning** — it's like having a senior bug hunter walk you through their thought process in real time.

---

## 🚀 Installation

### Prerequisites
```bash
# Required
python3 --version    # 3.8+
subfinder -version   # go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
httpx -version       # go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

### Setup
```bash
# Clone
git clone https://github.com/YOUR_USERNAME/vulnwhisper.git
cd vulnwhisper

# Virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Dependencies
pip install openai rich pyyaml

# Configure API key
cp .env.example .env
nano .env                       # Add your OpenRouter API key
```

### Get a Free API Key
1. Sign up at [openrouter.ai](https://openrouter.ai) — free, no credit card needed
2. Go to **API Keys** → create one
3. Paste it in your `.env` file

---

## 🔧 Configuration

Edit `config.yml` to customise behaviour:
```yaml
# Free models that work well:
# google/gemini-2.0-flash-thinking-exp:free
# nvidia/nemotron-3-super-120b-a12b:free
# meta-llama/llama-3.3-70b-instruct:free

model: nvidia/nemotron-3-super-120b-a12b:free
openrouter_base_url: https://openrouter.ai/api/v1
max_iterations: 30
request_timeout: 20
```

---

## 📋 Example Report Output
```markdown
# VulnWhisper Report

**Target:** admin.example.com
**Generated:** 2026-03-22 14:30:00
**Findings:** 3

## Summary
| Severity | Count |
|----------|-------|
| HIGH     | 1     |
| MEDIUM   | 1     |
| INFO     | 1     |

## Findings

### 1. Exposed GraphQL Introspection [HIGH]
**Detail:** GraphQL endpoint accepts introspection queries...
**Evidence:** {"data":{"__schema":{"types":[...
```

---

## ⚠️ Legal Disclaimer

> VulnWhisper is intended for **authorized security testing only**.
> Only use this tool against targets you have **explicit written permission** to test.
> The authors assume no liability for misuse or damage caused by this tool.
> Always comply with the program's scope and rules of engagement.

---

## 🗺️ Roadmap

- [ ] Nuclei integration for CVE scanning
- [ ] JavaScript endpoint extraction
- [ ] Wayback Machine historical URL analysis  
- [ ] IDOR detection via parameter fuzzing
- [ ] Multi-domain batch mode
- [ ] HTML report with charts
- [ ] Slack/Telegram alert integration
- [ ] Docker support

---

## 🤝 Contributing

PRs are welcome. If you have a tool that belongs in a hunter's arsenal, open an issue first to discuss.

---

## 📄 License

MIT © 2026 — Built with 🔥 by [YOUR_NAME](https://github.com/YOUR_USERNAME)

