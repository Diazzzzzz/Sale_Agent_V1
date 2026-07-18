"""节点档案 ⑦ 商务谈判。
客户试驾满意、进入谈价。给一版透明报价 + 当期限时优惠，推进成交。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="negotiation",
    name="商务谈判",
    goal="客户试驾满意、进入谈价阶段；目标是给一版清晰报价 + 当期优惠，推进下订成交。",
    advance_to="已提车",
    dialogue_guidance=(
        "报价透明：车价/优惠/金融/赠品分项列清。用限时政策制造合理紧迫感，不虚高不乱降；"
        "守住底线的同时给足诚意，落点=促成下订。"
    ),
    tools=["quote_offer"],
    timing="热线索，当日响应；优惠临期提醒，别拖凉。",
)
