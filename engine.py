"""Sales Agent 引擎：五步循环(感知 → 策划 → 生成 → 执行 → 回写)。
这是所有节点的『共同底座』，只写一次；节点只是喂进来的档案(NodeProfile)。
阶段一(增强人)：生成话术后停下，暂存 pending_action 等销售确认，不自动触达。"""
import json
from llm import chat
from perceive import perceive
from tools.model_comparison import REGISTRY as TOOLS
from config import PHASE

PLAN_SYSTEM = """你是汽车销售策略脑。给定客户状态和当前节点目标，规划本轮跟进。
只输出 JSON：
{"goal":"本轮目标","need_tool":true/false,"tool":"工具名或空字符串","tool_args":{...},"talking_points":["要点1","要点2"]}"""

GEN_SYSTEM = """你是资深汽车销售顾问。根据要点和工具结果，写一条发给客户的微信话术。
要求：人话、口语、真诚；聚焦客户在意点；不堆参数；一次只推进一步。直接输出话术正文，不要解释。"""


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
        f"工具结果：{json.dumps(tool_result, ensure_ascii=False)}\n\n请写话术。"
    )
    return chat(GEN_SYSTEM, user, mock_hint="generate")


def run_once(state, conversation, behaviors, profile):
    """跑一轮引擎五步。返回 (更新后的 state, 生成的话术)。"""
    # ① 感知
    print("① 感知 …")
    p = perceive(conversation, behaviors)
    state.hwc, state.current_node = p["hwc"], p["node"]
    print(f"   → HWC={p['hwc']}  节点={p['node']}  依据：{p['evidence']}")

    # ② 策划(目标/对话/内容&工具/时机)
    print("② 策划 …")
    plan = _plan(state, profile)
    print(f"   → 目标：{plan['goal']}  用工具：{plan['need_tool']}({plan.get('tool') or '—'})")

    # 内容&工具：需要就调工具
    tool_result = None
    if plan.get("need_tool") and plan.get("tool") in TOOLS:
        args = plan.get("tool_args") or {"budget": state.budget, "concerns": state.concerns}
        tool_result = TOOLS[plan["tool"]](**args)
        state.candidate_models = [c["model"] for c in tool_result.get("comparison", [])]
        print(f"   → 调用工具 {plan['tool']}，得到 {len(tool_result.get('comparison', []))} 款候选")

    # ③ 生成
    print("③ 生成 …")
    msg = _generate(state, plan, tool_result)

    # ④ 执行(阶段一：不真发，暂存等销售确认)
    print("④ 执行 …")
    if PHASE == "1":
        state.pending_action = {"type": "outreach", "channel": "wechat", "content": msg}
        print("   → 阶段一(增强人)：生成完毕，暂存 pending_action，待销售确认后再发。")
    else:
        print("   → 阶段二(自动)：直接触达。(MVP 未接真实发送通道)")

    # ⑤ 回写
    print("⑤ 回写 …")
    state.history.append(f"目标[{plan['goal']}] → 已生成话术，待确认")
    print("   → 客户状态已更新。")
    return state, msg
