"""通知模块（支持飞书 webhook）"""
from __future__ import annotations
import json
import os
from urllib.request import urlopen, Request


def _get_webhook(env_name: str) -> str:
    """从环境变量获取 webhook URL"""
    return os.environ.get(env_name, "")


def _send_feishu_card(card: dict, webhook_url: str) -> bool:
    """发送飞书卡片消息"""
    if not webhook_url:
        print("  [INFO] 未配置 webhook，跳过通知")
        return False
    try:
        data = json.dumps(card, ensure_ascii=False).encode("utf-8")
        req = Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                return True
            print(f"  [WARN] 飞书返回: {result}")
            return False
    except Exception as e:
        print(f"  [WARN] 飞书通知失败: {e}")
        return False


def _build_feishu_card(
    profile_name: str,
    new_papers: list[dict],
    stats: dict,
    errors: list[str] | None = None,
) -> dict:
    """构建飞书卡片消息"""
    total = stats.get("total", 0)
    by_label = stats.get("by_label", {})
    core_count = by_label.get("core", 0)
    strong_count = by_label.get("strongly_related", 0)

    if errors:
        header_color = "red"
        title = f"❌ {profile_name} — 搜索出错"
        elements = [
            {"tag": "markdown", "content": "\n".join(f"• {e}" for e in errors)}
        ]
    elif not new_papers:
        header_color = "grey"
        title = f"📋 {profile_name} — 今日无新增"
        elements = [
            {"tag": "markdown", "content": f"**总论文数**: {total}\n**核心**: {core_count} | **高相关**: {strong_count}"},
        ]
    else:
        header_color = "green"
        title = f"📚 {profile_name} — 新增 {len(new_papers)} 篇论文"
        paper_lines = []
        for p in new_papers[:10]:
            label_icon = {"core": "🔥", "strongly_related": "📎"}.get(p.get("quality_label", ""), "📝")
            title_text = p.get("title", "")[:50]
            url = p.get("url", "#")
            authors = ", ".join(p.get("authors", [])[:2])
            score = p.get("relevance_score", 0)
            cit = p.get("citation_count", 0)
            venue = p.get("venue", "")
            summary = p.get("summary_zh", "")[:60]
            line = f"{label_icon} [{title_text}]({url})\n"
            line += f"  作者: {authors} | 分数: {score} | 引用: {cit}"
            if venue:
                line += f" | 会议: {venue}"
            if summary:
                line += f"\n  📝 {summary}"
            paper_lines.append(line)
        content = f"**总论文数**: {total} | 核心: {core_count} | 高相关: {strong_count}\n\n"
        content += "\n\n".join(paper_lines)
        if len(new_papers) > 10:
            content += f"\n\n... 还有 {len(new_papers) - 10} 篇"
        elements = [{"tag": "markdown", "content": content}]

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": header_color,
            },
            "elements": elements,
        },
    }


def send_notification(
    profile_name: str,
    new_papers: list[dict],
    stats: dict,
    webhook_env: str = "",
    errors: list[str] | None = None,
) -> bool:
    """发送通知（入口函数）"""
    if not webhook_env:
        print("  [INFO] 未配置 webhook_env，跳过通知")
        return False
    webhook_url = _get_webhook(webhook_env)
    if not webhook_url:
        print(f"  [INFO] 环境变量 {webhook_env} 未设置，跳过通知")
        return False
    card = _build_feishu_card(profile_name, new_papers, stats, errors)
    return _send_feishu_card(card, webhook_url)
