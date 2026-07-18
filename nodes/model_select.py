"""节点档案 ④ 明确车型。
预算已定，客户要在【本品牌】车型里挑。结合在意点，在预算内缩到 1~2 款候选。
注意：这是“自家车里挑”，与 ⑤ 对比竞品(本品牌 vs 竞品)是两码事。"""
from nodes.base import NodeProfile

PROFILE = NodeProfile(
    node_id="model_select",
    name="明确车型",
    goal="客户预算已明确、车型未定；目标是结合在意点，在预算内把候选缩到 1~2 款本品牌车型。",
    advance_to="对比竞品",
    dialogue_guidance=(
        "在自家车型里做有取舍的推荐，别一次推太多。结合在意点讲清版本/配置/价格差异，"
        "用人话帮他缩到 1~2 款，落点邀到店实车对比。"
    ),
    tools=["model_select"],
    timing="比选期，2~3 天跟进一次；有新互动即时响应。",
)
