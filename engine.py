"""Sales Agent 引擎。
职责分层（关键）：
  ① 感知     perceive     读输入 → HWC 分级 + 节点
  ② 策略(军师) _plan       只做决策：定目标、决定调哪些/几个子agent、要产出什么、时机、要点。绝不写话术。
  ③ 执行·调用  _execute    按军师的 actions 逐个调用子agent/工具，收集结果
  ④ 执行·生成  _generate   按 deliverables 写面向客户的话术（这才是动笔的地方）
  ⑤ 回写/待确认            阶段一：暂存 pending_action，销售确认才触达

军师不上战场：策略层只规划，执行层才调工具、才写话术。

- run_engine(): 只算不打印，返回结构化结果 —— 给网页/上层用。
- run_once():   命令行版，跑 run_engine 再打印各步。
"""
import json
from llm import chat
from perceive import perceive
from tools import ALL_TOOLS as TOOLS
from config import PHASE

# ② 军师：只决策，不写话术
PLAN_SYSTEM = """你是汽车销售的『军师』(策略层)。你只做决策与规划，绝不撰写任何面向客户的话术。
根据客户状态与当前节点目标，规划本轮跟进。只输出 JSON：
{
  "goal": "本轮要达成的目标",
  "actions": [{"tool": "要调用的子agent/工具名(必须在可用工具里)", "why": "为什么调"}],
  "deliverables": ["本轮要产出什么，如：一条邀约到店的微信话术"],
  "timing": "跟进时机/节奏",
  "talking_points": ["给执行层的要点角度(短句，不是成段话术)"]
}
不需要调用工具时 actions 给空数组 []。严禁在任何字段里写面向客户的成段话术。"""

# ④ 执行·生成：这里才写话术
GEN_SYSTEM = """你是资深汽车销售顾问。请按军师给的目标、要点角度和工具结果，写一条发给客户的微信话术。
要求：人话、口语、真诚；针对客户在意点；我方短板主动找补不回避；不堆参数；落点是邀约到店。直接输出话术正文。"""


def _plan(state, profile) -> dict:
    """② 军师：产出作战计划(纯决策)。"""
    user = (
        f"客户状态：\n{state.to_json()}\n\n"
        f"当前节点：{profile.name}\n目标：{profile.goal}\n"
        f"话术指引：{profile.dialogue_guidance}\n可用工具：{profile.tools}\n\n"
        f"请规划本轮跟进（只做决策，不要写话术）。"
    )
    plan = json.loads(chat(PLAN_SYSTEM, user, json_mode=True, mock_hint="plan"))
    plan.setdefault("actions", [])
    plan.setdefault("deliverables", [])
    plan.setdefault("talking_points", [])
    return plan


def _execute(state, plan) -> list:
    """③ 执行·调用：按军师的 actions 逐个调子agent/工具，收集结果。"""
    results = []
    for act in plan.get("actions", []):
        tool = act.get("tool")
        if tool in TOOLS:
            results.append({"tool": tool, "why": act.get("why", ""), "result": TOOLS[tool](state)})
    return results


def _generate(state, plan, tool_results) -> str:
    """④ 执行·生成：按 deliverables 写话术。"""
    payload = [x["result"] for x in tool_results]
    user = (
        f"客户在意点：{state.concerns}\n本轮目标：{plan.get('goal')}\n"
        f"要产出：{plan.get('deliverables')}\n要点角度：{plan.get('talking_points')}\n"
        f"工具结果：{json.dumps(payload, ensure_ascii=False)}\n\n请写这条话术。"
    )
    return chat(GEN_SYSTEM, user, mock_hint="generate")


def run_engine(state, conversation, behaviors, profile, perceived=None) -> dict:
    """跑引擎，返回结构化结果(不打印)。
    perceived 传入时跳过①感知(用于无 key 的占位演示)。"""
    # ① 感知 + 客户分级
    if perceived is None:
        perceived = perceive(conversation, behaviors)
    state.hwc = perceived.get("hwc", state.hwc)
    state.current_node = perceived.get("node", state.current_node)

    # ② 策略(军师)：只决策
    plan = _plan(state, profile)

    # ③ 执行·调用子agent/工具（入参=state，工具自取，不信任 LLM 编的参数）
    tool_results = _execute(state, plan)

    # ④ 执行·生成话术
    msg = _generate(state, plan, tool_results)

    # ⑤ 回写 / 待确认（阶段一：不真发）
    if PHASE == "1":
        state.pending_action = {"type": "outreach", "channel": "wechat", "content": msg}
    state.history.append(f"目标[{plan.get('goal')}] → 已生成话术，待确认")

    return {"perceive": perceived, "plan": plan, "tool_results": tool_results,
            "message": msg, "phase": PHASE}


def run_once(state, conversation, behaviors, profile, perceived=None):
    """命令行版：跑引擎并打印各步。返回 (state, 生成的话术)。"""
    r = run_engine(state, conversation, behaviors, profile, perceived)
    p, plan = r["perceive"], r["plan"]

    print("① 感知 · 客户分级 …")
    print(f"   → HWC={p['hwc']}  节点={p['node']}  依据：{p.get('evidence', '')}")
    print("② 策略(军师) · 只决策不写话术 …")
    print(f"   → 目标：{plan.get('goal')}")
    tools = [a.get('tool') for a in plan.get('actions', [])]
    print(f"   → 决定调用子agent：{tools or '（本轮不调）'}")
    print(f"   → 要产出：{plan.get('deliverables')}   时机：{plan.get('timing', '')}")
    print("③ 执行 · 调用子agent …")
    for x in r["tool_results"]:
        n = len(x["result"].get("dimensions", []))
        print(f"   → {x['tool']}：得到 {n} 个对比维度")
    if not r["tool_results"]:
        print("   → （本轮无工具调用）")
    print("④ 执行 · 生成话术 …")
    print("   → 已生成（见下）")
    print("⑤ 待确认 …")
    if r["phase"] == "1":
        print("   → 阶段一(增强人)：暂存 pending_action，待销售确认后再发。")
    else:
        print("   → 阶段二(自动)：直接触达。(MVP 未接真实发送通道)")
    return state, r["message"]
