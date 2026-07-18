"""OmniSA · Sales Agent 八节点演示网页。

顶部一条八节点导航：认可品牌 → 了解产品 → 明确预算 → 明确车型 → 对比竞品 →
到店试驾 → 商务谈判 → 已提车。点任一节点，看该节点下 Agent 跑的一整套引擎五步。

两种模式（同一套代码）：
  · 静态/mock(无 key)：直接渲染每个剧本预置的 demo，八条路径稳定好看、不烧 token。发布传播用这个。
  · 真跑(配了 DEEPSEEK/火山 key)：走 engine.run_engine()，感知/军师/话术现算。
「▶ 现场跑」输入框走 /api/run：观众自己输入客户对话，现场看 Agent 跑（需真跑模式）。

运行：  python web.py  →  http://127.0.0.1:5001   （PORT=xxxx 可改）
"""
import os
from flask import Flask, render_template, request, jsonify, abort

from state import CustomerState
from engine import run_engine
from nodes import NODES, get_profile
from demo_scenarios import SCENARIOS, list_scenarios, parse_dialogue, scenario_for_node
from config import PROVIDERS, ACTIVE_PROVIDER

app = Flask(__name__)


def _mock_mode() -> bool:
    """没配当前供应商的 key → 静态/mock 模式。"""
    return not os.getenv(PROVIDERS[ACTIVE_PROVIDER]["api_key_env"])


def _state_from_scenario(sc) -> CustomerState:
    st = CustomerState(
        customer_id=sc["customer_id"],
        budget=sc.get("budget", ""),
        intent_car=sc.get("intent_car", ""),
        rival_car=sc.get("rival_car", ""),
        concerns=sc.get("concerns", []),
    )
    # 车型图：挂到 state 上，工具桩会取用（真跑模式下工具卡也带图）
    st.image = sc.get("image")
    return st


def _result_for(sc, mock: bool) -> dict:
    """产出统一的引擎五步结果。mock→用剧本预置 demo；真跑→跑引擎。"""
    if mock:
        d = sc["demo"]
        return {"perceive": d["perceive"], "plan": d["plan"],
                "tool_results": d["tool_results"], "message": d["message"],
                "phase": os.getenv("SA_PHASE", "1"), "source": "static"}
    state = _state_from_scenario(sc)
    profile = get_profile(sc["node_id"])
    r = run_engine(state, sc["transcript"], sc.get("behaviors", ""), profile, perceived=None)
    r["source"] = "live"
    return r


@app.route("/")
@app.route("/s/<sid>")
def chat(sid=None):
    scenarios = list_scenarios()
    if not sid:
        sid = scenarios[0]["id"]
    sc = SCENARIOS.get(sid)
    if not sc:
        abort(404)

    mock = _mock_mode()
    result = _result_for(sc, mock)
    profile = get_profile(sc["node_id"])

    return render_template(
        "chat.html",
        scenarios=scenarios, current=sid, sc=sc,
        dialogue=parse_dialogue(sc["transcript"]),
        r=result, profile=profile,
        nodes=[{"node_id": p.node_id, "name": p.name} for p in NODES],
        mock_mode=mock, provider=ACTIVE_PROVIDER,
    )


@app.route("/api/run", methods=["POST"])
def api_run():
    """现场跑：观众自己输入客户对话 + 选节点 → 跑引擎，返回五步 JSON。
    真跑模式(配了 key)现算；静态模式回落到该节点的预置 demo，并提示需配 key。"""
    data = request.get_json(force=True, silent=True) or {}
    node_id = data.get("node_id") or NODES[0].node_id
    transcript = (data.get("transcript") or "").strip()
    profile = get_profile(node_id)
    if not profile:
        return jsonify({"error": f"未知节点：{node_id}"}), 400

    mock = _mock_mode()
    if mock:
        sid = scenario_for_node(node_id)
        demo = SCENARIOS[sid]["demo"] if sid else None
        return jsonify({
            "live": False,
            "notice": "当前是静态演示模式：现场真跑需配置模型 key(DEEPSEEK_API_KEY 或火山)。下面先给您看该节点的预置示例。",
            "result": demo,
        })

    # 真跑：用观众输入的对话，缺输入就用该节点样板对话兜底
    sid = scenario_for_node(node_id)
    base = SCENARIOS.get(sid, {})
    state = _state_from_scenario(base) if base else CustomerState(customer_id="C_LIVE")
    convo = transcript or base.get("transcript", "")
    r = run_engine(state, convo, base.get("behaviors", ""), profile, perceived=None)
    r["live"] = True
    return jsonify({"live": True, "result": r})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=True)
