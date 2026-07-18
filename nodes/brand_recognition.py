"""节点档案 ① 认可品牌。
客户还没建立品牌信任(常拿合资/大牌做锚)，先破“不如它”的心结，再谈产品。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="brand_recognition",
    name="认可品牌",
    goal="客户尚未认可品牌、常拿合资或大牌做对比；目标是用硬事实打消“不如它”的顾虑，"
         "建立对品牌的初步信任，让他愿意进一步了解产品。",
    advance_to="了解产品",
    dialogue_guidance=(
        "客户还没建立品牌信任，别急着讲车、堆参数。用销量/保有量/权威奖项/真实车主口碑做背书，"
        "把“专业/独立品牌 ≠ 杂牌”讲清楚；真诚、不吹，落点是邀他到店眼见为实。"
    ),
    tools=["brand_proof"],
    timing="冷线索，3~5 天轻触一次，不逼单，先建立信任。",
)
