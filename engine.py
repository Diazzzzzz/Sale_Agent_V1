"""Sales Agent 引擎：五步循环(感知 → 策划 → 生成 → 执行 → 回写)。
这是所有节点的『共同底座』，只写一次；节点只是喂进来的档案(NodeProfile)。
阶段一(增强人)：生成话术后停下，暂存 pending_action 等销售确认，不自动触达。

- run_engine(): 只算不打印，返回结构化结果 —— 给网页/其它上层用。
- run_once():   命令行版，跑 run_engine 再打印五步。
"""
import json
from llm import chat
from perceive import perceive
from tools.model_comparison import REGISTRY as TOOLS
from config import PHASE

PLAN_SYSTEM = """你是汽车销售策略脑。给定客户状态和当前节点目标，规划本轮跟进。
只输出 JSON：
{"goal":"本轮目标","need_tool":true/false,"tool":"工具名或空字符串","talking_points":["要点1","要点2"]}"""

GEN_SYSTEM = """你是资深汽车销售顾问。根据要点和工具给的对比结果，写一条发给客户的微信话术。
要求：人话、口语、真诚；针对客户在意点；我方短板主动找补不回避；不堆参数；落点是邀约到店。直接输出话术正文。"""


def _plan(state, profile) -> dict:
    user = (
        f"客户状态：\n{state.to_json()}\n\n"
        f"当前节点：{profile.name}\n目标：{profile.goal}\n"
        f"话术指引：{profile.dialogue_guidance}\n可用工具：{profile.tools}\n\n"
        f"请规划本轮跟进。"
    )
    return json.loads(chat(PLAN_SYSTEM, user, json_mode=True, mock_hint="plan"))


def _generate(state, plan, tool_result) -> str:
    user = (
        f"客户在意点：{state.concerns}\n本轮目标：{plan['goal']}\n"
        f"要点：{plan['talking_points']}\n"
        f"车型对比结果：{json.dumps(tool_result, ensure_ascii=False)}\n\n请写话术。"
    )
    return chat(GEN_SYSTEM, user, mock_hint="generate")


def run_engine(state, conversation, behaviors, profile, perceived=None) -> dict:
    """跑引擎五步，返回结构化结果(不打印)。
    perceived 传入时跳过①感知(用于无 key 的 mock 演示，直接用剧本给定的状态)。"""
    # ① 感知
    if perceived is None:
        perceived = perceive(conversation, behaviors)
    state.hwc = perceived.get("hwc", state.hwc)
    state.current_node = perceived.get("node", state.current_node)

    # ② 策划（目标/对话/内容&工具/时机）
    plan = _plan(state, profile)

    # 内容&工具：需要就调工具。工具入参 = 整个 state（工具自取，不信任 LLM 编的参数）
    tool_result = None
    if plan.get("need_tool") and plan.get("tool") in TOOLS:
        tool_result = TOOLS[plan["tool"]](state)

    # ③ 生成
    msg = _generate(state, plan, tool_result)

    # ④ 执行（阶段一：不真发，暂存等销售确认）
    if PHASE == "1":
        state.pending_action = {"type": "outreach", "channel": "wechat", "content": msg}

    # ⑤ 回写
    state.history.append(f"目标[{plan['goal']}] → 已生成话术，待确认")

    return {"perceive": perceived, "plan": plan, "tool_result": tool_result,
            "message": msg, "phase": PHASE}


def run_once(state, conversation, behaviors, profile, perceived=None):
    """命令行版：跑引擎并打印五步。返回 (state, 生成的话术)。"""
    r = run_engine(state, conversation, behaviors, profile, perceived)
    p, plan = r["perceive"], r["plan"]

    print("① 感知 …")
    print(f"   → HWC={p['hwc']}  节点={p['node']}  依据：{p.get('evidence', '')}")
    print("② 策划 …")
    print(f"   → 目标：{plan['goal']}  用工具：{plan.get('need_tool')}({plan.get('tool') or '—'})")
    if r["tool_result"]:
        n = len(r["tool_result"].get("dimensions", []))
        print(f"   → 调用工具 {plan.get('tool')}，得到 {n} 个对比维度")
    print("③ 生成 …")
    print("④ 执行 …")
    if r["phase"] == "1":
        print("   → 阶段一(增强人)：生成完毕，暂存 pending_action，待销售确认后再发。")
    else:
        print("   → 阶段二(自动)：直接触达。(MVP 未接真实发送通道)")
    print("⑤ 回写 …")
    print("   → 客户状态已更新。")
    return state, r["message"]
