"""节点档案 ⑧ 已提车。
客户已成交提车。做好交付关怀提升满意度，再自然引出转介绍。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="delivered",
    name="已提车",
    goal="客户已成交提车；目标是做好交付关怀、提升满意度，并自然邀约转介绍。",
    advance_to="售后关怀(闭环)",
    dialogue_guidance=(
        "先真诚关怀(用车提醒/首保/答疑)，再自然引出转介绍激励，不功利、不硬推；"
        "落点=邀请推荐亲友并说明老带新好处。"
    ),
    tools=["care_referral"],
    timing="提车后 3 天回访，首保前提醒，做节点式长期关怀。",
)
