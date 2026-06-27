# 🎯 Paper Hunter

通用学术论文自动搜集、评分、归档、通知系统。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建 Profile

在 `profiles/` 目录下创建 JSON 配置文件：

```json
{
  "profile_name": "My Research Domain",
  "description": "我的研究领域论文自动搜集",
  "output_dir": "output/my_domain",
  "queries": {
    "core": ["关键词1", "关键词2"],
    "expanded": ["扩展关键词1"],
    "exploratory": ["探索性关键词1"]
  },
  "domain_keywords": ["领域词1", "领域词2"],
  "filters": {
    "years_from": 2020,
    "years_to": 2027,
    "allowed_categories": ["cs.CV", "cs.AI"],
    "blocked_keywords": ["无关词1"]
  },
  "scoring": {
    "min_relevance_score": 2.5,
    "core_threshold": 4.0
  },
  "notification": {
    "type": "feishu",
    "webhook_env": "MY_WEBHOOK_ENV"
  }
}
```

### 3. 运行

```bash
# 每日搜集
python -m paper_hunter.cli run-daily profiles/my_domain.json
```

## 📊 Profile 配置说明

| 字段 | 说明 | 必填 |
|------|------|------|
| `profile_name` | 配置名称 | ✅ |
| `description` | 描述 | ❌ |
| `output_dir` | 输出目录（相对于项目根目录） | ❌ (默认 `papers`) |
| `queries.core` | 核心查询词 | ✅ |
| `queries.expanded` | 扩展查询词 | ❌ |
| `queries.exploratory` | 探索性查询词 | ❌ |
| `domain_keywords` | 领域关键词（命中加分） | ❌ |
| `filters.years_from` | 起始年份 | ❌ (默认 2015) |
| `filters.years_to` | 结束年份 | ❌ (默认 2027) |
| `filters.allowed_categories` | 允许的 arXiv 类别 | ❌ |
| `filters.blocked_keywords` | 屏蔽关键词（命中扣分） | ❌ |
| `scoring.min_relevance_score` | 最低相关性分数 | ❌ (默认 2.5) |
| `scoring.core_threshold` | Core 论文阈值 | ❌ (默认 4.0) |
| `notification.type` | 通知类型 (feishu/none) | ❌ |
| `notification.webhook_env` | Webhook 环境变量名 | ❌ |

## 🔔 飞书通知

设置环境变量：

```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

## 📁 输出结构

```
output/
└── my_domain/
    └── index.jsonl          # 论文索引（JSONL 格式）
```

## 🧪 测试

```bash
python -m pytest -q
```

## 📄 License

MIT
