"""节点档案 ⑥ 到店试驾。
客户有明确意向却迟迟没到店。制造到店理由 + 给具体时段二选一，促成到店试驾。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="test_drive",
    name="到店试驾",
    goal="客户意向明确但一直没到店；目标是促成一次有具体时间的到店试驾。",
    advance_to="商务谈判",
    dialogue_guidance=(
        "制造到店理由(实车/试驾/专属优惠/到店礼)，给两三个具体时段让他二选一、降低决策成本，"
        "确认车辆已备好，落点=约定一个具体时间。"
    ),
    tools=["test_drive_booking"],
    timing="热线索，快速跟进；约定后临期再提醒一次。",
)
