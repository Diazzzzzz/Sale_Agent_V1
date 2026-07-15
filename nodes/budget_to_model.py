"""节点档案 #1：明确预算 → 明确车型。
第一个跑通的节点，用来证明『1 引擎 + 1 档案 + 1 工具』整条链路成立。
它挂着 model_comparison 工具(任务2会把桩换成真的车型对比 Agent)。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="budget_to_model",
    name="明确预算 → 明确车型",
    goal="客户预算已明确、但车型未定；目标是帮他在预算内锁定 1~2 款候选车型。",
    advance_to="明确车型",
    dialogue_guidance=(
        "客户已有预算，别再反复问预算。聚焦『预算内哪几款值得看』。"
        "结合客户在意点(concerns)做有取舍的推荐，用人话讲清差异，不堆参数。"
        "自然引出车型对比，降低客户的选择成本，一次只推进一步。"
    ),
    tools=["model_comparison"],
    timing="客户处于比选期，2~3 天跟进一次；有新互动即时响应。",
)
