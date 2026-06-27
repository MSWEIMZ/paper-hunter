# 🎯 Paper Hunter

通用学术论文自动搜集、评分、归档、通知系统。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化配置

```bash
python -m paper_hunter.cli init
```

向导会引导你完成配置：
1. 选择研究领域（8 个预设模板或自定义）
2. 确认/修改关键词
3. 配置飞书通知（可选）
4. 设置年份范围

完成后自动生成 `profiles/xxx.json`。

### 3. 推送到 GitHub

```bash
git add profiles/xxx.json
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

## 🔔 飞书通知

向导会提示你输入飞书 Webhook URL。

如果跳过，可以手动设置环境变量：
```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

## 📊 手动运行

```bash
# 每日搜集
python -m paper_hunter.cli run-daily profiles/video.json
```

## 📁 输出结构

```
output/
└── video/
    └── index.jsonl          # 论文索引（JSONL 格式）
```

## 🧪 测试

```bash
python -m pytest -q
```

## 📄 License

MIT
