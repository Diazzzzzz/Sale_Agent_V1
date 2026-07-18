"""节点档案 ② 了解产品。
客户认了牌子，但不知道这款车好在哪。按在意点挑 2~3 个核心卖点讲透，种草。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="product_intro",
    name="了解产品",
    goal="客户已认可品牌但不了解这款车的优势；目标是围绕他的在意点讲清 2~3 个核心卖点，"
         "让他被种草、愿意深入了解。",
    advance_to="明确预算",
    dialogue_guidance=(
        "别把全部配置一股脑倒出来。挑客户在意点对应的 2~3 个亮点讲透，用场景化人话"
        "(带娃/通勤/越野)，配亮点图，落点引导到“这款正适合您，来看看实车”。"
    ),
    tools=["product_highlight"],
    timing="温线索，2~4 天跟进一次，围绕在意点持续种草。",
)
