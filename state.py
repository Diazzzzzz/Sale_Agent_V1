"""客户工作态(state)：Sales Agent 的记忆与身份。
这是一份很薄的『状态契约』——MVP 只放跑起来必需的字段；
以后画像库(10表/23标签)定稿，直接插进来，引擎无需改动。"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class CustomerState:
    customer_id: str
    current_node: str = "未知"           # 当前八节点位置（感知判出）
    hwc: str = "C"                       # 热度 H/W/C/O/S（感知判出）
    budget: str = ""                     # 预算档位
    intent_car: str = ""                 # 客户意向的我方车型（对比竞品节点要用）
    rival_car: str = ""                  # 客户在纠结的竞品车型
    candidate_models: List[str] = field(default_factory=list)  # 候选车型
    concerns: List[str] = field(default_factory=list)          # 在意点
    history: List[str] = field(default_factory=list)           # 近几轮摘要
    pending_action: Optional[dict] = None                      # 待销售确认的动作

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, path: str) -> "CustomerState":
        with open(path, encoding="utf-8") as f:
            return cls(**json.load(f))
