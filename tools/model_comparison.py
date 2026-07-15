"""车型对比 Agent —— 工具桩(stub)。
被引擎当作工具调用，返回结构化对比结果。
任务2会把这里换成真的：接车型内容库，输出『人话 + 聚焦客户在意点 + 可信、不堆参数』。"""


def model_comparison(budget: str, concerns=None, candidates=None) -> dict:
    concerns = concerns or []
    candidates = candidates or ["车型A", "车型B"]
    # TODO(任务2): 替换为真实车型对比 Agent（接内容库/画像库，按 concerns 聚焦）
    return {
        "budget": budget,
        "focus": concerns,
        "comparison": [
            {"model": candidates[0], "亮点": "空间大、家用舒适、油耗低", "取舍": "动力偏家用"},
            {"model": candidates[1], "亮点": "动力足、配置高、驾驶感好", "取舍": "后排略小、油耗略高"},
        ],
        "note": "这是工具桩输出；任务2接入真实内容库后替换。",
    }


# 工具注册表：引擎按名字查用
REGISTRY = {"model_comparison": model_comparison}
