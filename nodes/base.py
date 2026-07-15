"""节点档案(NodeProfile)：引擎的『剧本』。
共同底座是引擎(engine.py)，只写一次；每个节点的差异只是一份档案(数据/配置)。
加新节点 = 加一份档案，不写引擎代码 —— 这就是『底座长分支、扩到10个只加2份档案』。"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class NodeProfile:
    node_id: str
    name: str
    goal: str                 # 本节点要把客户推进到哪
    advance_to: str           # 达成后进入的下一节点
    dialogue_guidance: str    # 喂给策略脑的话术指引(prompt 片段)
    tools: List[str] = field(default_factory=list)  # 本节点可调用的工具
    timing: str = ""          # 时机/频次规则
