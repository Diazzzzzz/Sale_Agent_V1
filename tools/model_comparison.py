"""车型对比工具 —— 桩(stub)。
本品牌意向车 vs 客户纠结的竞品，按客户在意点给出有取舍的对比。
入参是整个 state（工具自己从状态里取所需，避免引擎/LLM 传错参数）。

任务2的真车型对比 Agent 已在另一个仓库(Model_Comparison_Agent)，
并留好了口子 `POST /api/compare`。接入时把本函数替换成调用那个口子即可，
引擎/节点/状态都不用改。见 docs 或 Model_Comparison_Agent/docs/接口_口子.md。
"""

# 演示用的维度目录：按在意点命中，给"我方占优/竞品更强(带找补)"的条目
_CATALOG = {
    "安全": {"ours": "全系6气囊 + L2 辅助驾驶", "rival": "基础主动安全",
             "winner": "ours", "comment": "带娃出行更放心"},
    "空间": {"ours": "轴距更长、后备箱更能装", "rival": "够用但偏小",
             "winner": "ours", "comment": "推车、大件都塞得下"},
    "油耗": {"ours": "综合油耗中等水平", "rival": "更省一点",
             "winner": "rival", "comment": "找补：差距不大，月供更低能摊平"},
    "保值": {"ours": "国产保值率近年快速提升", "rival": "合资保值率偏高",
             "winner": "rival", "comment": "找补：算上落地价差 + 长质保，几年持有成本更低"},
    "价格": {"ours": "同配置指导价更低", "rival": "偏高",
             "winner": "ours", "comment": "钱花在配置和用料上"},
    "配置": {"ours": "大屏车机 + 智能座舱更丰富", "rival": "中规中矩",
             "winner": "ours", "comment": "日常好用、有面子"},
}


def model_comparison(state) -> dict:
    our = state.intent_car or "我方车型"
    rival = state.rival_car or "竞品车型"
    concerns = state.concerns or ["综合表现"]

    dims, used = [], set()
    for c in concerns:                       # 先按客户在意点命中
        for key, v in _CATALOG.items():
            if key in c and key not in used:
                dims.append(_row(our, rival, key, v)); used.add(key); break
    for key in ("安全", "空间", "保值"):       # 不足3条补默认，保证有取舍
        if len(dims) >= 3:
            break
        if key not in used:
            dims.append(_row(our, rival, key, _CATALOG[key])); used.add(key)

    top = concerns[0] if concerns else "综合表现"
    return {
        "our_car": our,
        "rival_car": rival,
        "summary": f"同价位下，{our} 在你最看重的「{top}」上更占优；个别短板可用月供/质保找补。",
        "dimensions": dims,
        "_stub": True,   # 标记：这是桩数据，接真口子后替换
    }


def _row(our, rival, name, v):
    return {"name": name, "ours": f"{our}：{v['ours']}", "rival": f"{rival}：{v['rival']}",
            "winner": v["winner"], "comment": v["comment"]}


# 工具注册表：引擎按名字查用
REGISTRY = {"model_comparison": model_comparison}
