"""OmniSA · Sales Agent 八节点演示网页。

单列聊天式：点顶部任一节点，页面把该节点下 Agent 的一轮跑，
逐句/逐步「播放」出来 —— 客户对话一句句冒出 → 感知 → 军师 → 工具 → 话术 → 待确认。

两种模式（同一套代码）：
  · 静态/mock(无 key)：渲染每个剧本预置的引擎五步，稳定好看、不烧 token。
  · 真跑(配了 DEEPSEEK/火山 key)：走 engine.run_engine()，感知/军师/话术现算。

运行：  python web.py  →  http://127.0.0.1:5001   （PORT=xxxx 可改）
"""
import os
from flask import Flask, render_template, abort

from state import CustomerState
from engine import run_engine
from nodes import get_profile
from demo_scenarios import SCENARIOS, list_scenarios, parse_dialogue
from config import PROVIDERS, ACTIVE_PROVIDER

app = Flask(__name__)


def _mock_mode() -> bool:
    """没配当前供应商的 key → 静态/mock 模式。"""
    return not os.getenv(PROVIDERS[ACTIVE_PROVIDER]["api_key_env"])


def _result_for(sc, mock: bool) -> dict:
    """产出统一的引擎五步结果。mock→用剧本预置 demo；真跑→跑引擎。"""
    if mock:
        d = sc["demo"]
        return {"perceive": d["perceive"], "plan": d["plan"],
                "tool_results": d["tool_results"], "message": d["message"],
                "phase": os.getenv("SA_PHASE", "1")}
    state = CustomerState(
        customer_id=sc["customer_id"], budget=sc.get("budget", ""),
        intent_car=sc.get("intent_car", ""), rival_car=sc.get("rival_car", ""),
        concerns=sc.get("concerns", []))
    state.image = sc.get("image")
    return run_engine(state, sc["transcript"], sc.get("behaviors", ""),
                      get_profile(sc["node_id"]), perceived=None)


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
    return render_template(
        "chat.html",
        scenarios=scenarios, current=sid, sc=sc,
        dialogue=parse_dialogue(sc["transcript"]),
        r=_result_for(sc, mock),
        mock_mode=mock, provider=ACTIVE_PROVIDER,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=True)
