<p align="center">
  <strong>English</strong> | <a href="README_zh.md">中文</a>
</p>

<h1 align="center">
🎯 Paper Hunter
</h1>

<p align="center">
  <strong>Automated academic paper discovery, scoring, archiving & notification</strong>
</p>

<p align="center">
  <a href="https://github.com/MSWEIMZ/paper-hunter/actions"><img src="https://img.shields.io/github/actions/workflow/status/MSWEIMZ/paper-hunter/daily_search.yml?label=Daily%20Search&logo=github-actions&logoColor=white" alt="CI"></a>
  <a href="https://github.com/MSWEIMZ/paper-hunter"><img src="https://img.shields.io/github/stars/MSWEIMZ/paper-hunter?style=social" alt="Stars"></a>
  <a href="https://github.com/MSWEIMZ/paper-hunter/blob/master/LICENSE"><img src="https://img.shields.io/github/license/MSWEIMZ/paper-hunter" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-52%20passed-brightgreen" alt="Tests">
</p>

<p align="center">
  📚 <a href="https://github.com/MSWEIMZ/video-cnn-interpretability"><b>Live Example</b></a> — Video CNN/XAI Research Hub (445+ papers)
</p>

---

## ✨ Features

| Feature | Description |
|:--------|:------------|
| 🎯 **Multi-Source Search** | arXiv, Semantic Scholar, OpenAlex, CrossRef + custom APIs |
| 🧠 **Smart Scoring** | 4D scoring: Relevance · Novelty · Impact · Hotness |
| 📊 **Auto Dashboard** | README, Topics, Trends, HTML dashboard with charts |
| 🔔 **Multi-Channel Notify** | Feishu · Telegram · Email |
| 🏆 **Top K Daily Picks** | Auto-select the most worth-reading papers |
| 🔧 **Zero-Code Setup** | Interactive wizard with 8 preset templates |
| 📄 **BibTeX Export** | One-click export to `.bib` format |
| ⏰ **GitHub Actions** | Daily automated search & push |

---

## 🚀 Quick Start

```
paper-hunter/
├── src/paper_hunter/          # Core modules
│   ├── collector.py           # Multi-source paper collector
│   ├── scorer.py              # 4D scoring engine
│   ├── normalizer.py          # Paper record normalization
│   ├── storage.py             # JSONL index storage
│   ├── summarizer.py          # Summary enhancement
│   ├── topics.py              # Topic clustering
│   ├── readme.py              # Auto README generator
│   ├── dashboard.py           # HTML dashboard (Chart.js)
│   ├── trends.py              # Trend report
│   ├── topk.py                # Top K daily picks
│   ├── citation_filler.py     # CrossRef citation backfill
│   ├── notify.py              # Feishu / Telegram / Email
│   └── cli.py                 # CLI entry point
├── profiles/                  # User configurations
└── output/                    # Generated outputs
    └── {profile}/
        ├── index.jsonl        # Paper index
        ├── README.md          # Paper list
        ├── TOPICS.md          # Topic clustering
        ├── TRENDS.md          # Trend report
        ├── TOP_K.md           # Daily top picks
        ├── dashboard.html     # Visual dashboard
        └── papers.bib         # BibTeX export
```

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Setup (interactive wizard)

```bash
python -m paper_hunter.cli init
```

The wizard guides you through 8 steps:

```
Step 1 ─ Choose domain          ─┐
Step 2 ─ Core keywords           │  Preset templates
Step 3 ─ Extended keywords       │  or custom input
Step 4 ─ Notification channel  ──┘  (Feishu / Telegram / Email)
Step 5 ─ Year range
Step 6 ─ Data sources            ── arXiv, Semantic Scholar, OpenAlex, custom
Step 7 ─ Search schedule
Step 8 ─ Top K picks per day
```

### 3. Push & Go

```bash
git add profiles/xxx.json sources.json
git commit -m "add my profile"
git push
```

GitHub Actions runs daily. Papers appear in your Feishu / Telegram / Email. 🎉

---

## 📋 Preset Templates

| Template | Domain | Keywords Preview |
|:--------:|:-------|:-----------------|
| `video` | Video Understanding | video understanding, action recognition, 3D CNN |
| `vision` | Computer Vision | image classification, object detection, segmentation |
| `nlp` | NLP | text classification, machine translation, QA |
| `llm` | Large Language Models | LLM, instruction tuning, prompt engineering |
| `medical` | Medical Imaging | medical image segmentation, radiology AI |
| `robotics` | Robot Learning | robot manipulation, reinforcement learning |
| `diffusion` | Diffusion Models | diffusion model, text-to-image, video generation |
| `xai` | Explainable AI | Grad-CAM, saliency map, attention visualization |

---

## 🧠 4D Scoring System

```
                    ┌─────────────────────────────────────┐
                    │         Composite Score              │
                    │                                      │
                    │   ┌──────────┐   ┌──────────┐       │
                    │   │Relevance │   │ Novelty  │       │
                    │   │  40%     │   │  20%     │       │
                    │   └──────────┘   └──────────┘       │
                    │   ┌──────────┐   ┌──────────┐       │
                    │   │ Impact   │   │ Hotness  │       │
                    │   │  25%     │   │  15%     │       │
                    │   └──────────┘   └──────────┘       │
                    └─────────────────────────────────────┘

  Relevance   keyword match + venue + survey bonus
  Novelty     exponential decay by paper age
  Impact      log10(citations) / log10(10000)
  Hotness     recent citation velocity
```

---

## 📊 CLI Commands

| Command | Description |
|:--------|:------------|
| `python -m paper_hunter.cli init` | 🎯 Interactive setup wizard |
| `python -m paper_hunter.cli run-daily <profile>` | 📥 Daily paper search |
| `python -m paper_hunter.cli run-backfill <profile>` | 🔄 Backfill citation data |
| `python -m paper_hunter.cli run-stats <profile>` | 📊 View statistics |
| `python -m paper_hunter.cli run-export <profile>` | 📄 Export BibTeX |

---

## 🔔 Notification Channels

<details>
<summary>🔔 Feishu (飞书)</summary>

```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```
</details>

<details>
<summary>📱 Telegram</summary>

```bash
export TG_BOT_TOKEN="your-bot-token"
export TG_CHAT_ID="your-chat-id"
```
</details>

<details>
<summary>📧 Email (SMTP)</summary>

Configure in profile JSON:
```json
{
  "notification": {
    "type": "email",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "you@gmail.com",
    "to_email": "you@gmail.com"
  }
}
```
</details>

---

## ❓ FAQ

<details>
<summary>How do I add a custom data source?</summary>

Run `python -m paper_hunter.cli init` and follow Step 6, or manually edit `sources.json`:

```json
{
  "custom": [{
    "name": "PubMed",
    "api_url": "https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pubmed/",
    "query_param": "title",
    "format": "json",
    "title_field": "data.title",
    "abstract_field": "data.abstract",
    "max_results": 20
  }]
}
```
</details>

<details>
<summary>How do I change the search schedule?</summary>

Edit the `cron` expression in `.github/workflows/daily_search.yml`. GitHub Actions schedules are defined by the workflow file and use UTC.
</details>

<details>
<summary>Can I use multiple profiles?</summary>

Yes! Just create multiple JSON files in `profiles/`. GitHub Actions will run all of them.
</details>

<details>
<summary>How do I backfill citations?</summary>

```bash
python -m paper_hunter.cli run-backfill profiles/xxx.json
```

Uses CrossRef API (free, no rate limit).
</details>

---

## 📄 License

MIT

<p align="center">
  🤖 Powered by <a href="https://github.com/MSWEIMZ/paper-hunter">Paper Hunter</a>
</p>
