#!/usr/bin/env python3
"""把 8 个中文场景批量翻译成目标语言，缓存到 i18n_cache.json。
占位模式据此整页离线切换语言；真跑模式输入/标签也用它，输出仍现算。

跑法（需配 key，和真跑同一个）：
    python scripts/build_i18n.py            # 翻译 en ru es fr 全部
    python scripts/build_i18n.py en es      # 只翻这几种
改了中文场景后重跑即可覆盖更新。node/hwc/tool 名等枚举不翻（保持匹配）。
"""
import os, sys, json, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_scenarios import SCENARIOS, parse_dialogue
from config import LANGUAGES, PROVIDERS, ACTIVE_PROVIDER
from llm import chat

TARGETS = [a for a in sys.argv[1:] if a in LANGUAGES and a != "zh"] or ["en", "ru", "es", "fr"]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "i18n_cache.json")

# 不翻译的键（保持枚举/匹配/结构）
KEEP = {"hwc", "node", "tool", "card_type", "winner", "_stub", "image", "role", "node_id"}


def translatable(sid, sc):
    """抽出该场景要翻译的显示字段（含结构），dialogue 带 role/who。"""
    d = sc["demo"]
    return {
        "title": sc["title"], "intent_car": sc.get("intent_car", ""),
        "rival_car": sc.get("rival_car", ""), "budget": sc.get("budget", ""),
        "concerns": sc.get("concerns", []),
        "dialogue": parse_dialogue(sc["transcript"]),
        "demo": {
            "perceive": d["perceive"],
            "plan": d["plan"],
            "tool_results": d["tool_results"],
            "message": d["message"],
        },
    }


SYS = """You are a professional localizer for an automotive sales SaaS demo.
Translate ALL human-readable Chinese strings in the given JSON into {lang_name} ({country}),
using the car-sales business language and tone customary in {country}.
{guide}

HARD RULES:
- Return ONLY a JSON object with the EXACT same structure and keys as the input.
- Do NOT translate or change these keys' values: hwc, node, tool, card_type, winner, _stub, image, role, node_id. Keep them byte-for-byte.
- Translate every other string value (title, texts, evidence, goal, why, deliverables, timing, talking_points, summary, labels, values, notes, message, the customer/sales speaker label 'who', etc.).
- Keep car model names as their official local names where they exist (e.g. 长城坦克300 -> GWM Tank 300), otherwise transliterate sensibly.
- LOCALIZE THE CUSTOMER'S NAME: replace the Chinese personal name with a common given name / surname typical of {country}. Use the SAME person consistently across the title, every dialogue 'text', and the message (e.g. the greeting). The salesperson label stays a generic word for "Sales".
- LOCALIZE PRICES REALISTICALLY: for any price / budget / monthly payment, use a plausible CURRENT market figure for THIS vehicle in {country}, in the local currency — do NOT do a literal digit-for-digit swap of the Chinese amount. Keep placeholder tokens like XX, XX.XX, N unchanged.
- Keep it natural, like a real local salesperson wrote it."""


DEMO_KEYS = ("perceive", "plan", "tool_results", "message")


def _valid(tr):
    """译文结构是否完整（demo 四键齐全）。"""
    return isinstance(tr, dict) and all(k in tr.get("demo", {}) for k in DEMO_KEYS)


def build_lang(lang, tries=3):
    cfg = LANGUAGES[lang]
    system = (SYS.format(lang_name=cfg["name"], country=cfg["country"], guide=cfg["guide"])
              + "\n- CRITICAL: 'demo' MUST keep exactly these top-level keys: perceive, plan, tool_results, message. "
                "Do NOT nest plan/tool_results/message inside perceive.")
    out = {}
    for sid, sc in SCENARIOS.items():
        src = translatable(sid, sc)
        user = "Translate this JSON:\n" + json.dumps(src, ensure_ascii=False)
        tr, ok = None, False
        for _ in range(tries):
            try:
                tr = json.loads(chat(system, user, json_mode=True))
                _restore_keys(src, tr)
                if _valid(tr):
                    ok = True
                    break
            except Exception as e:
                tr = {"_err": str(e)}
        if ok:
            out[sid] = tr
            print(f"  [{lang}] {sid} ✓")
        else:
            # 结构翻不对：保留中文 demo（输入/标签仍是译文），绝不写坏结构
            tr = tr if isinstance(tr, dict) else {}
            tr["demo"] = copy.deepcopy(src["demo"])
            for k in ("title", "intent_car", "rival_car", "budget", "concerns", "dialogue"):
                tr.setdefault(k, src.get(k))
            out[sid] = tr
            print(f"  [{lang}] {sid} ⚠ 结构漂移，demo 保留中文")
    return out


def _restore_keys(src, tr):
    """递归把 KEEP 键的值从原文强制拷回译文，防结构/枚举漂移。"""
    if isinstance(src, dict) and isinstance(tr, dict):
        for k, v in src.items():
            if k in KEEP:
                tr[k] = v
            elif k in tr:
                _restore_keys(v, tr[k])
    elif isinstance(src, list) and isinstance(tr, list) and len(src) == len(tr):
        for a, b in zip(src, tr):
            _restore_keys(a, b)


def main():
    if not os.getenv(PROVIDERS[ACTIVE_PROVIDER]["api_key_env"]):
        print("⚠️ 没检测到模型 key：请先 set -a; source .env; set +a（或 export DEEPSEEK_API_KEY=...）再跑。")
        sys.exit(1)
    cache = {}
    if os.path.exists(OUT):
        cache = json.load(open(OUT, encoding="utf-8"))
    for lang in TARGETS:
        print(f"== 翻译 {lang} ({LANGUAGES[lang]['country']}) ==")
        cache[lang] = build_lang(lang)
    json.dump(cache, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"✅ 写入 {OUT}，语言：{list(cache.keys())}")


if __name__ == "__main__":
    main()
