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


# ---- mock：无 key 时的占位输出，仅为跑通链路 ----
def _mock(hint):
    if hint == "perceive":
        return json.dumps({
            "hwc": "W",
            "node": "明确预算",
            "evidence": "预算已明确(20万)但车型未定，属1~3月内考虑的温线索",
        }, ensure_ascii=False)
    if hint == "plan":
        return json.dumps({
            "goal": "在20万预算内帮客户锁定1~2款家用SUV候选",
            "need_tool": True,
            "tool": "model_comparison",
            "tool_args": {"budget": "20万", "concerns": ["空间", "油耗"]},
            "talking_points": ["聚焦空间和油耗", "给2款有取舍的候选", "用对比降低选择成本"],
        }, ensure_ascii=False)
    if hint == "generate":
        return (
            "哥，按您说的20万预算、主要家里用，还看重空间和油耗，我给您圈了两款重点：\n"
            "一款空间和舒适更好，接送孩子、周末出游都从容；另一款动力更足、配置更高，日常开着更带劲。\n"
            "我把它俩的空间、油耗、用车成本摆一块儿做了个对比，您扫一眼就知道哪款更贴合，\n"
            "要不我发您看看？省得您到处翻参数。"
        )
    return "(mock)"
