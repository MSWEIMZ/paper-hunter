[English](README.md) | **中文**

# 🎯 Paper Hunter

通用学术论文自动搜集、评分、归档、通知系统。

> **实际案例**：[Video CNN/XAI Research Hub](https://github.com/MSWEIMZ/video-cnn-interpretability) — 基于 Paper Hunter 构建的视频理解与可解释性论文库，收录 445+ 篇论文。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化配置

```bash
python -m paper_hunter.cli init
```

向导会引导你完成配置（7 步）：
1. 选择研究领域（8 个预设模板或自定义）
2. 确认/修改核心关键词
3. 确认/修改扩展关键词
4. 配置飞书通知（可选）
5. 设置年份范围
6. 选择数据源（arXiv/Semantic Scholar/OpenAlex/自定义）
7. 设置搜索时间

完成后自动生成 `profiles/xxx.json` 和 `sources.json`。

### 3. 推送到 GitHub

```bash
git add profiles/xxx.json sources.json
git commit -m "add my profile"
git push
```

GitHub Actions 将每天自动运行，论文推送到飞书。

## 📋 预设模板

| 模板 | 说明 |
|------|------|
| `video` | 视频理解与分析 |
| `vision` | 计算机视觉 |
| `nlp` | 自然语言处理 |
| `llm` | 大语言模型 |
| `medical` | 医学影像 |
| `robotics` | 机器人学习 |
| `diffusion` | 扩散模型 |
| `xai` | 可解释 AI |

## 🔔 通知方式

### 飞书

向导会提示你输入飞书 Webhook URL。也可以手动设置：
```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### 邮件（SMTP）

在 profile 中配置：
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

## 📊 CLI 命令

```bash
# 交互式初始化向导
python -m paper_hunter.cli init

# 每日搜集
python -m paper_hunter.cli run-daily profiles/video.json

# 回填引用数据（CrossRef）
python -m paper_hunter.cli run-backfill profiles/video.json

# 查看统计信息
python -m paper_hunter.cli run-stats profiles/video.json

# 导出 BibTeX
python -m paper_hunter.cli run-export profiles/video.json
```

## 📁 输出结构

```
output/
└── video/
    ├── index.jsonl          # 论文索引（JSONL 格式）
    ├── README.md            # 自动生成的论文列表
    ├── TOPICS.md            # 主题聚类统计
    ├── TRENDS.md            # 趋势报告
    ├── dashboard.html       # 可视化看板（Chart.js）
    └── papers.bib           # BibTeX 导出
```

## 🧪 测试

```bash
python -m pytest -q
```

## 📄 License

MIT
