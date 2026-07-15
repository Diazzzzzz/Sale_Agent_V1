"""Sales Agent · 网页聊天演示。
展示真·Sales Agent 在跑：对话逐句展开 → 引擎感知 HWC/节点 →
到「对比竞品」节点调用车型对比工具 → 对比卡嵌进聊天 → 生成话术停在"待销售确认"。

运行：  python web.py   →  打开 http://127.0.0.1:5000
无 key 走 mock（用剧本自带的感知结果）；配 DeepSeek key 则感知/生成走真模型。
"""
import os
from flask import Flask, render_template, abort

from state import CustomerState
from engine import run_engine
from nodes.rival_compare import PROFILE
from demo_scenarios import SCENARIOS, list_scenarios, parse_dialogue
from config import PROVIDERS, ACTIVE_PROVIDER

app = Flask(__name__)


def _mock_mode() -> bool:
    """没配当前供应商的 key → mock 模式。"""
    return not os.getenv(PROVIDERS[ACTIVE_PROVIDER]["api_key_env"])


@app.route("/")
@app.route("/s/<sid>")
def chat(sid=None):
    scenarios = list_scenarios()
    if not sid:
        sid = scenarios[0]["id"]
    sc = SCENARIOS.get(sid)
    if not sc:
        abort(404)

    state = CustomerState(
        customer_id=sc["customer_id"],
        budget=sc["budget"],
        intent_car=sc["intent_car"],
        rival_car=sc["rival_car"],
        concerns=sc["concerns"],
    )

    mock = _mock_mode()
    perceived = sc.get("perceived") if mock else None
    result = run_engine(state, sc["transcript"], sc.get("behaviors", ""), PROFILE, perceived=perceived)

    return render_template(
        "chat.html",
        scenarios=scenarios, current=sid, sc=sc,
        dialogue=parse_dialogue(sc["transcript"]),
        state=state, r=result, node=PROFILE.name, mock_mode=mock,
        provider=ACTIVE_PROVIDER,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
