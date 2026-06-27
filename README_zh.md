<p align="center">
  <a href="README.md">English</a> | <strong>中文</strong>
</p>

<h1 align="center">
🎯 Paper Hunter
</h1>

<p align="center">
  <strong>通用学术论文自动搜集、评分、归档、通知系统</strong>
</p>

<p align="center">
  <a href="https://github.com/MSWEIMZ/paper-hunter/actions"><img src="https://img.shields.io/github/actions/workflow/status/MSWEIMZ/paper-hunter/daily_search.yml?label=Daily%20Search&logo=github-actions&logoColor=white" alt="CI"></a>
  <a href="https://github.com/MSWEIMZ/paper-hunter"><img src="https://img.shields.io/github/stars/MSWEIMZ/paper-hunter?style=social" alt="Stars"></a>
  <a href="https://github.com/MSWEIMZ/paper-hunter/blob/master/LICENSE"><img src="https://img.shields.io/github/license/MSWEIMZ/paper-hunter" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-52%20passed-brightgreen" alt="Tests">
</p>

<p align="center">
  📚 <a href="https://github.com/MSWEIMZ/video-cnn-interpretability"><b>实际案例</b></a> — Video CNN/XAI Research Hub（445+ 篇论文）
</p>

---

## ✨ 核心功能

| 功能 | 说明 |
|:-----|:-----|
| 🎯 **多源搜索** | arXiv、Semantic Scholar、OpenAlex、CrossRef + 自定义 API |
| 🧠 **4D 评分** | 相关性 · 新颖性 · 影响力 · 热度 四维度评分 |
| 📊 **自动看板** | README、主题聚类、趋势报告、HTML 看板 |
| 🔔 **多渠道通知** | 飞书 · Telegram · 邮件 |
| 🏆 **Top K 推荐** | 每日自动挑选最值得读的论文 |
| 🔧 **零代码配置** | 交互式向导 + 8 个预设模板 |
| 📄 **BibTeX 导出** | 一键导出 `.bib` 格式 |
| ⏰ **GitHub Actions** | 每日自动搜索 & 推送 |

---

## 🚀 快速开始

```
paper-hunter/
├── src/paper_hunter/          # 核心模块
│   ├── collector.py           # 多源论文收集器
│   ├── scorer.py              # 4D 评分引擎
│   ├── normalizer.py          # 论文结构标准化
│   ├── storage.py             # JSONL 索引存储
│   ├── summarizer.py          # 摘要增强
│   ├── topics.py              # 主题聚类
│   ├── readme.py              # README 自动生成
│   ├── dashboard.py           # HTML 看板（Chart.js）
│   ├── trends.py              # 趋势报告
│   ├── topk.py                # Top K 每日推荐
│   ├── citation_filler.py     # CrossRef 引用回填
│   ├── notify.py              # 飞书 / Telegram / 邮件
│   └── cli.py                 # CLI 入口
├── profiles/                  # 用户配置
└── output/                    # 生成输出
    └── {profile}/
        ├── index.jsonl        # 论文索引
        ├── README.md          # 论文列表
        ├── TOPICS.md          # 主题聚类
        ├── TRENDS.md          # 趋势报告
        ├── TOP_K.md           # 每日推荐
        ├── dashboard.html     # 可视化看板
        └── papers.bib         # BibTeX 导出
```

### 1. 安装

```bash
pip install -r requirements.txt
```

### 2. 初始化（交互式向导）

```bash
python -m paper_hunter.cli init
```

向导引导你完成 8 步配置：

```
第 1 步 ─ 选择研究领域        ─┐
第 2 步 ─ 核心关键词           │  预设模板
第 3 步 ─ 扩展关键词           │  或自定义
第 4 步 ─ 通知方式           ──┘  （飞书 / Telegram / 邮件）
第 5 步 ─ 年份范围
第 6 步 ─ 数据源             ── arXiv、Semantic Scholar、OpenAlex、自定义
第 7 步 ─ 搜索时间
第 8 步 ─ 每日推荐数量
```

### 3. 推送 & 完成

```bash
git add profiles/xxx.json sources.json
git commit -m "add my profile"
git push
```

GitHub Actions 每天自动运行，论文推送到飞书 / Telegram / 邮件 🎉

---

## 📋 预设模板

| 模板 | 领域 | 关键词预览 |
|:----:|:-----|:-----------|
| `video` | 视频理解 | video understanding, action recognition, 3D CNN |
| `vision` | 计算机视觉 | image classification, object detection, segmentation |
| `nlp` | 自然语言处理 | text classification, machine translation, QA |
| `llm` | 大语言模型 | LLM, instruction tuning, prompt engineering |
| `medical` | 医学影像 | medical image segmentation, radiology AI |
| `robotics` | 机器人学习 | robot manipulation, reinforcement learning |
| `diffusion` | 扩散模型 | diffusion model, text-to-image, video generation |
| `xai` | 可解释 AI | Grad-CAM, saliency map, attention visualization |

---

## 🧠 4D 评分系统

```
                    ┌─────────────────────────────────────┐
                    │           综合评分                   │
                    │                                      │
                    │   ┌──────────┐   ┌──────────┐       │
                    │   │ 相关性   │   │ 新颖性   │       │
                    │   │  40%     │   │  20%     │       │
                    │   └──────────┘   └──────────┘       │
                    │   ┌──────────┐   ┌──────────┐       │
                    │   │ 影响力   │   │  热度    │       │
                    │   │  25%     │   │  15%     │       │
                    │   └──────────┘   └──────────┘       │
                    └─────────────────────────────────────┘

  相关性   关键词匹配 + 会议加分 + 综述加分
  新颖性   年份指数衰减（当年=1.0，去年=0.8）
  影响力   log₁₀(引用数) / log₁₀(10000)
  热度     近期引用增速
```

---

## 📊 CLI 命令

| 命令 | 说明 |
|:-----|:-----|
| `python -m paper_hunter.cli init` | 🎯 交互式初始化向导 |
| `python -m paper_hunter.cli run-daily <profile>` | 📥 每日论文搜集 |
| `python -m paper_hunter.cli run-backfill <profile>` | 🔄 回填引用数据 |
| `python -m paper_hunter.cli run-stats <profile>` | 📊 查看统计信息 |
| `python -m paper_hunter.cli run-export <profile>` | 📄 导出 BibTeX |

---

## 🔔 通知方式

<details>
<summary>🔔 飞书</summary>

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
<summary>📧 邮件（SMTP）</summary>

在 profile JSON 中配置：
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

## ❓ 常见问题

<details>
<summary>如何添加自定义数据源？</summary>

运行 `python -m paper_hunter.cli init` 按第 6 步操作，或手动编辑 `sources.json`：

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
<summary>如何修改搜索时间？</summary>

编辑 `profiles/xxx.json` → `schedule.cron`，或重新运行 `init` 向导第 7 步。
</details>

<details>
<summary>可以同时使用多个 profile 吗？</summary>

可以！在 `profiles/` 目录下创建多个 JSON 文件，GitHub Actions 会逐个运行。
</details>

<details>
<summary>如何回填引用数据？</summary>

```bash
python -m paper_hunter.cli run-backfill profiles/xxx.json
```

使用 CrossRef API（免费、无限速）。
</details>

---

## 📄 License

MIT

<p align="center">
  🤖 Powered by <a href="https://github.com/MSWEIMZ/paper-hunter">Paper Hunter</a>
</p>
