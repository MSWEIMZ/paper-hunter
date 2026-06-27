**English** | [中文](README_zh.md)

# 🎯 Paper Hunter

Automated academic paper discovery, scoring, archiving & notification system.

> **Live Example**: [Video CNN/XAI Research Hub](https://github.com/MSWEIMZ/video-cnn-interpretability) — 445+ papers on video understanding & explainability, powered by Paper Hunter.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Configuration

```bash
python -m paper_hunter.cli init
```

The wizard will guide you through:
1. Choose research domain (8 preset templates or custom)
2. Confirm/modify keywords
3. Configure Feishu webhook (optional)
4. Set year range
5. Choose data sources
6. Set search schedule

### 3. Push to GitHub

```bash
git add profiles/xxx.json sources.json
git commit -m "add my profile"
git push
```

GitHub Actions will run daily and push papers to your Feishu.

## 📋 Preset Templates

| Template | Description |
|----------|-------------|
| `video` | Video Understanding & Analysis |
| `vision` | Computer Vision |
| `nlp` | Natural Language Processing |
| `llm` | Large Language Models |
| `medical` | Medical Imaging |
| `robotics` | Robot Learning |
| `diffusion` | Diffusion Models |
| `xai` | Explainable AI |

## 🔔 Notifications

### Feishu

The wizard will prompt you for a Feishu Webhook URL. Or set manually:
```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### Email (SMTP)

Configure in your profile:
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

## 📊 CLI Commands

```bash
# Interactive setup wizard
python -m paper_hunter.cli init

# Daily paper search
python -m paper_hunter.cli run-daily profiles/video.json

# Backfill citation data (CrossRef)
python -m paper_hunter.cli run-backfill profiles/video.json

# View statistics
python -m paper_hunter.cli run-stats profiles/video.json

# Export BibTeX
python -m paper_hunter.cli run-export profiles/video.json
```

## 📁 Output Structure

```
output/
└── video/
    ├── index.jsonl          # Paper index (JSONL)
    ├── README.md            # Auto-generated paper list
    ├── TOPICS.md            # Topic clustering
    ├── TRENDS.md            # Trend report
    ├── dashboard.html       # Visual dashboard (Chart.js)
    └── papers.bib           # BibTeX export
```

## 🧪 Testing

```bash
python -m pytest -q
```

## 📄 License

MIT
