"""八节点注册表：按购车旅程顺序排列。
这是「1 引擎 + N 节点档案」里的 N —— 加节点 = 加一份档案 + 在这里登记一行，引擎不改。

顺序即 perceive.py 里的八节点：
  认可品牌 → 了解产品 → 明确预算 → 明确车型 → 对比竞品 → 到店试驾 → 商务谈判 → 已提车
"""
from nodes.brand_recognition import PROFILE as _n1
from nodes.product_intro import PROFILE as _n2
from nodes.budget_clarify import PROFILE as _n3
from nodes.model_select import PROFILE as _n4
from nodes.rival_compare import PROFILE as _n5
from nodes.test_drive import PROFILE as _n6
from nodes.negotiation import PROFILE as _n7
from nodes.delivered import PROFILE as _n8

# 有序列表：网页顶部导航按这个顺序画八节点
NODES = [_n1, _n2, _n3, _n4, _n5, _n6, _n7, _n8]

# 按 node_id / 节点名 都能查到档案
BY_ID = {p.node_id: p for p in NODES}
BY_NAME = {p.name: p for p in NODES}


def get_profile(key: str):
    """按 node_id 或中文节点名取档案；取不到返回 None。"""
    return BY_ID.get(key) or BY_NAME.get(key)
