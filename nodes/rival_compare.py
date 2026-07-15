"""节点档案 · 对比竞品（Sales Agent 的 flagship 演示节点）。
客户在【我方意向车】和【竞品】之间摇摆时，用车型对比帮他坚定选择。
这是车型对比工具的正确归属节点（本品牌 vs 竞品）。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="rival_compare",
    name="对比竞品",
    goal="客户在我方意向车与竞品之间纠结；目标是用有取舍、可信的对比帮他坚定选我方，并邀约到店试驾。",
    advance_to="到店试驾",
    dialogue_guidance=(
        "客户已在比价，别再泛泛介绍。直接针对『我方意向车 vs 他纠结的竞品』，"
        "围绕客户的在意点(concerns)讲清差异；我方短板要主动承认并找补，别回避，"
        "这样更可信。用人话，不堆参数，落点是邀约到店实车感受。"
    ),
    tools=["model_comparison"],
    timing="客户处于比价决策期，节奏要快，2天内跟进一次；有新互动即时响应。",
)
