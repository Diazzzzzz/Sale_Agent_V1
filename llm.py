"""LLM 调用层：统一封装，DeepSeek / 火山引擎可切。
无 API key 时自动降级为 mock，逻辑照样跑通(方便先看流程，再接真模型)。"""
import os
import json
from config import PROVIDERS, ACTIVE_PROVIDER, TEMPERATURE


def _client():
    """返回 (client, cfg)；没配 key 时 client=None → 走 mock。"""
    cfg = PROVIDERS[ACTIVE_PROVIDER]
    key = os.getenv(cfg["api_key_env"])
    if not key:
        return None, cfg
    from openai import OpenAI  # 延迟导入：mock 模式无需安装 openai
    return OpenAI(api_key=key, base_url=cfg["base_url"]), cfg


def chat(system, user, json_mode=False, mock_hint=None):
    """一次对话调用。json_mode=True 时要求模型返回 JSON。"""
    client, cfg = _client()
    if client is None:
        return _mock(mock_hint)

    kwargs = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": TEMPERATURE,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


# ---- mock：无 key 时的占位输出，仅为跑通链路（对比竞品场景）----
def _mock(hint):
    if hint == "perceive":
        return json.dumps({
            "hwc": "H",
            "node": "对比竞品",
            "evidence": "客户已在我方意向车与竞品之间比价，主动询问差异，属临近成交的热线索",
        }, ensure_ascii=False)
    if hint == "plan":
        return json.dumps({
            "goal": "帮客户在意向车与竞品之间坚定选我方，并邀约到店试驾",
            "actions": [{"tool": "model_comparison", "why": "客户在比价，需要有取舍的对比数据支撑"}],
            "deliverables": ["一条邀约到店试驾的微信话术"],
            "timing": "2天内跟进，有互动即时响应",
            "talking_points": ["紧扣客户在意点讲差异", "主动认短板并找补", "落点邀约到店实车感受"],
        }, ensure_ascii=False)
    if hint == "generate":
        return (
            "哥，您在这两款之间纠结我特别理解。我把咱们看的这款和您在比的那款，"
            "按您最在意的几点做了个对比：该占优的地方咱们确实更强；有一两项对手稍好，"
            "我也如实跟您说了，其实算上月供和质保是能找补回来的。\n"
            "光看参数没感觉，不如您抽空来店里，两台车我都给您备着，实车一坐一开就清楚了。您看这周末方便吗？"
        )
    return "(mock)"
