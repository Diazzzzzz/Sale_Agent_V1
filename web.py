"""OmniSA · Sales Agent 八节点演示网页。

单列聊天式：点顶部任一节点，页面把该节点下 Agent 的一轮跑，
逐句/逐步「播放」出来 —— 客户对话一句句冒出 → 感知 → 军师 → 工具 → 话术 → 待确认。

两种模式（同一套代码）：
  · 静态/mock(无 key)：渲染每个剧本预置的引擎五步，稳定好看、不烧 token。
  · 真跑(配了 DEEPSEEK/火山 key)：走 engine.run_engine()，感知/军师/话术现算。

运行：  python web.py  →  http://127.0.0.1:5001   （PORT=xxxx 可改）
"""
import os
import json
from flask import Flask, render_template, request, jsonify, abort

from state import CustomerState
from engine import run_engine, regenerate
from nodes import get_profile
from demo_scenarios import SCENARIOS, list_scenarios, parse_dialogue
from config import PROVIDERS, ACTIVE_PROVIDER, LANGUAGES, DEFAULT_LANG
from i18n import ui as ui_strings, NODE_NAMES, node_name

app = Flask(__name__)

# 场景译文缓存（scripts/build_i18n.py 生成）：{lang: {sid: {title,intent_car,...,dialogue,demo}}}
_CACHE_PATH = os.path.join(os.path.dirname(__file__), "i18n_cache.json")
try:
    with open(_CACHE_PATH, encoding="utf-8") as _f:
        I18N_CACHE = json.load(_f)
except (FileNotFoundError, ValueError):
    I18N_CACHE = {}


def _loc(sid, lang):
    """取某语言某场景的译文；中文或无缓存返回 None。"""
    if lang == "zh":
        return None
    return I18N_CACHE.get(lang, {}).get(sid)


def _lang_of(req) -> str:
    """从 ?lang= / POST lang 取语言，非法值回落默认。"""
    lang = (req.args.get("lang") if req.method == "GET" else (req.get_json(silent=True) or {}).get("lang")) or DEFAULT_LANG
    return lang if lang in LANGUAGES else DEFAULT_LANG


def _mode(req):
    """决定这次请求走占位还是真跑。
    真跑 = 顶部开关打开(live=1) 且 配了 key。默认关(占位)，安全、不烧 token。
    返回 (mock, live, has_key)。"""
    has_key = bool(os.getenv(PROVIDERS[ACTIVE_PROVIDER]["api_key_env"]))
    lp = req.args.get("live") if req.method == "GET" else (req.get_json(silent=True) or {}).get("live")
    live = (str(lp) == "1")          # 默认 OFF；显式 live=1 才开
    mock = not (live and has_key)
    return mock, live, has_key


def _state_of(sc) -> CustomerState:
    st = CustomerState(
        customer_id=sc["customer_id"], budget=sc.get("budget", ""),
        intent_car=sc.get("intent_car", ""), rival_car=sc.get("rival_car", ""),
        concerns=sc.get("concerns", []))
    st.image = sc.get("image")
    return st


def _result_for(sc, mock: bool, lang: str, loc) -> dict:
    """产出引擎五步结果。
    占位：用预置 demo——非中文且有译文缓存则用译文；真跑：按 lang 现跑引擎。"""
    if mock:
        d = (loc or sc)["demo"]
        return {"perceive": d["perceive"], "plan": d["plan"],
                "tool_results": d["tool_results"], "message": d["message"],
                "phase": os.getenv("SA_PHASE", "1")}
    return run_engine(_state_of(sc), sc["transcript"], sc.get("behaviors", ""),
                      get_profile(sc["node_id"]), perceived=None, lang=lang)


def _sc_view(sc, loc):
    """给模板用的场景视图：非中文且有译文则覆盖显示字段。"""
    if not loc:
        return sc
    v = dict(sc)
    for k in ("title", "intent_car", "rival_car", "budget", "concerns"):
        if k in loc:
            v[k] = loc[k]
    return v


@app.route("/")
@app.route("/s/<sid>")
def chat(sid=None):
    scenarios = list_scenarios()
    if not sid:
        sid = scenarios[0]["id"]
    sc = SCENARIOS.get(sid)
    if not sc:
        abort(404)

    mock, live, has_key = _mode(request)
    lang = _lang_of(request)
    loc = _loc(sid, lang)
    dialogue = loc["dialogue"] if (loc and loc.get("dialogue")) else parse_dialogue(sc["transcript"])
    return render_template(
        "chat.html",
        scenarios=scenarios, current=sid, sc=_sc_view(sc, loc),
        dialogue=dialogue,
        r=_result_for(sc, mock, lang, loc),
        mock_mode=mock, live=live, has_key=has_key, provider=ACTIVE_PROVIDER,
        languages=LANGUAGES, current_lang=lang,
        t=ui_strings(lang),
        nn=(lambda zh: node_name(lang, zh)),
        i18n_ready=list(I18N_CACHE.keys()),
    )


@app.route("/api/revise", methods=["POST"])
def api_revise():
    """⑤『改一版』：销售用自然语言提修改意见 → Agent 重写一版话术（只改④，不重播）。"""
    data = request.get_json(force=True, silent=True) or {}
    sid = data.get("sid")
    instruction = (data.get("instruction") or "").strip()
    sc = SCENARIOS.get(sid)
    if not sc:
        return jsonify({"error": "未知场景"}), 400
    if not instruction:
        return jsonify({"error": "请先输入修改意见"}), 400

    mock, live, has_key = _mode(request)
    if mock:
        if not has_key:
            notice = "未检测到模型 key：请在 .env 填 DEEPSEEK_API_KEY（或火山）并重启，再打开顶部『真跑模型』开关。"
        else:
            notice = "当前是占位演示：打开顶部『真跑模型』开关后，Agent 会按您的修改意见现场重写一版话术。"
        return jsonify({"live": False, "notice": notice})

    lang = _lang_of(request)
    d = sc["demo"]
    msg = regenerate(_state_of(sc), d["plan"], d["tool_results"], d["message"], instruction, lang)
    return jsonify({"live": True, "message": msg})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=True)
