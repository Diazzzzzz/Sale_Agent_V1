"""状态感知模块：客户对话/行为 → HWC 热度 + 八节点位置 + 判定依据。
是引擎五步的第一步『感知』，也可独立调用(先把这块跑通是最正确的第一块积木)。"""
import json
from llm import chat

SYSTEM = """你是汽车销售 SCRM 的客户状态分析器。依据 HWC 模型判定客户热度与购车节点。

HWC 热度：H 热(1周内成交)/W 温(1~3月考虑)/C 冷(3月+或未明确)/O 已下订/S 已交付。
判定：时间维度(预计购车时间)为核心第一判据；行为维度校准——主动到店/试驾/询价→升；长期无响应/仅浏览→降。

八节点(购买旅程进度，与热度正交)：
认可品牌 → 了解产品 → 明确预算 → 明确车型 → 对比竞品 → 到店试驾 → 商务谈判 → 已提车。

只输出 JSON：{"hwc":"H/W/C/O/S","node":"节点名","evidence":"一句话依据"}"""


def perceive(conversation: str, behaviors: str = None) -> dict:
    user = (
        f"对话记录：\n{conversation}\n\n"
        f"行为信号：\n{behaviors or '无'}\n\n"
        f"请判定该客户的 HWC 热度与所处节点。"
    )
    raw = chat(SYSTEM, user, json_mode=True, mock_hint="perceive")
    return json.loads(raw)
