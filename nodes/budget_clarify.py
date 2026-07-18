"""节点档案 ③ 明确预算。
客户喜欢车但预算模糊/纠结价格。用落地价+分期把“钱的事”讲透明，锚定预算。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="budget_clarify",
    name="明确预算",
    goal="客户对车有意向但预算模糊或纠结价格；目标是把落地价/月供算清、降低价格顾虑，"
         "帮他把预算锚定下来。",
    advance_to="明确车型",
    dialogue_guidance=(
        "不逼问预算。用“落地价试算 + 分期方案”把钱讲透明，给几档方案让他有掌控感；"
        "弱化总价、强调月供可承受，落点邀到店细谈。"
    ),
    tools=["finance_calc"],
    timing="温线索，2~3 天跟进；客户一问价立即响应。",
)
