"""其余七个节点的演示工具 —— 桩(stub)。
和 model_comparison 一样：入参是整个 state，工具自取所需，不信任 LLM 编的参数。
返回「通用卡」结构，供网页统一渲染：
    {
      "card_type": "generic",     # generic=通用条目卡；comparison=对比卡(见 model_comparison)
      "title":   "卡标题",
      "subtitle":"一句话说明",
      "image":   "havh6.jpg" 或 None,   # 车型/素材图文件名，放在 static/images/ 下；缺图自动占位
      "items":   [{"label":.., "value":.., "note":..}],
      "_stub":   True,            # 标记桩数据；接真内容库/画像库后替换
    }
真数据来源（接入时替换本函数体，节点/引擎/状态都不用改）：
    brand_proof     ← 内容库·品牌素材域
    product_highlight ← 内容库·卖点切片域(按 concern 命中)
    finance_calc    ← 金融方案表 / 落地价规则
    model_select    ← 内容库·车型主数据(本品牌内部选型)
    test_drive_booking ← DMS·门店排期
    quote_offer     ← 报价/优惠政策表
    care_referral   ← 售后·关怀 SOP + 转介绍激励
"""


def _card(title, subtitle, items, image=None):
    return {"card_type": "generic", "title": title, "subtitle": subtitle,
            "image": image, "items": items, "_stub": True}


# ① 认可品牌 —— 品牌实力/口碑背书
def brand_proof(state) -> dict:
    car = state.intent_car or "本品牌"
    return _card(
        title=f"{car} · 品牌实力背书",
        subtitle="用硬事实打消“不如合资/杂牌”的顾虑",
        image=_img(state),
        items=[
            {"label": "品类地位", "value": "细分市场销量领先", "note": "不是杂牌，是专业品牌"},
            {"label": "保有量", "value": "全球累计用户 XX 万", "note": "占位：填真实数字"},
            {"label": "权威认可", "value": "XX 碰撞测试五星 / 年度车型奖", "note": "占位：填真实奖项"},
            {"label": "车主口碑", "value": "满意度 XX%，真实提车作业 N 篇", "note": "占位：挂口碑素材"},
        ],
    )


# ② 了解产品 —— 按在意点挑核心卖点
def product_highlight(state) -> dict:
    car = state.intent_car or "这款车"
    concerns = state.concerns or ["综合表现"]
    hi = {
        "安全": {"value": "全系 6 气囊 + L2 辅助驾驶", "note": "带娃出行更放心"},
        "空间": {"value": "同级更长轴距，后排/后备箱能装", "note": "全家出行不憋屈"},
        "配置": {"value": "大屏智能座舱 + 丰富主动安全", "note": "日常好用有面子"},
        "越野": {"value": "非承载车身 + 四驱，专业越野基因", "note": "撒野也能应付"},
        "油耗": {"value": "同级主流油耗表现", "note": "日常通勤成本可控"},
        "外观": {"value": "方正硬派造型，辨识度高", "note": "停哪都有回头率"},
    }
    items = []
    for c in concerns[:3]:
        for k, v in hi.items():
            if k in c:
                items.append({"label": k, "value": v["value"], "note": v["note"]})
                break
    if not items:  # 兜底
        items = [{"label": "核心亮点", "value": hi["安全"]["value"], "note": hi["安全"]["note"]}]
    return _card(f"{car} · 为您挑的核心亮点", "只讲您在意的 2~3 点，不堆参数",
                 _img(state), items)


# ③ 明确预算 —— 落地价 / 分期试算
def finance_calc(state) -> dict:
    car = state.intent_car or "这款车"
    return _card(
        title=f"{car} · 落地价 & 分期试算",
        subtitle="把“钱的事”讲透明，弱化总价、强调月供可承受",
        image=_img(state),
        items=[
            {"label": "参考裸车价", "value": "XX.XX 万", "note": "占位：按实际车型填"},
            {"label": "落地价(含税险)", "value": "约 XX.XX 万", "note": "占位：一价清单"},
            {"label": "首付方案", "value": "低至 30% ≈ X.X 万", "note": "门槛可再谈"},
            {"label": "月供参考", "value": "约 X,XXX 元 / 月", "note": "分 36 期示例"},
        ],
    )


# ④ 明确车型 —— 本品牌内部选型(预算内缩到 1~2 款)
def model_select(state) -> dict:
    budget = state.budget or "您的预算"
    cands = state.candidate_models or ["候选车型A", "候选车型B"]
    items = []
    for i, m in enumerate(cands[:2]):
        items.append({"label": f"候选{i+1}", "value": m,
                      "note": "占位：版本/配置/价格差异一句话"})
    items.append({"label": "选型建议", "value": f"{budget} 内先锁这 1~2 款",
                  "note": "到店实车对比最快拍板"})
    return _card("为您在自家车型里缩个范围", "有取舍地推，不一次推太多",
                 _img(state), items)


# ⑥ 到店试驾 —— 预约卡(门店/时段/车辆)
def test_drive_booking(state) -> dict:
    car = state.intent_car or "意向车型"
    return _card(
        title="到店试驾 · 为您留车留时段",
        subtitle="给两三个具体时段二选一，降低到店决策成本",
        image=_img(state),
        items=[
            {"label": "试驾车型", "value": car, "note": "已为您备好实车"},
            {"label": "推荐时段", "value": "本周六 10:30 / 周日 15:00", "note": "二选一即可"},
            {"label": "门店", "value": "XX 品牌中心(占位：门店名/地址)", "note": "导航一键可达"},
            {"label": "到店礼", "value": "试驾即赠 XX(占位)", "note": "制造到店理由"},
        ],
    )


# ⑦ 商务谈判 —— 报价 / 优惠政策
def quote_offer(state) -> dict:
    car = state.intent_car or "意向车型"
    return _card(
        title=f"{car} · 本期报价单",
        subtitle="分项列清、限时政策，诚意透明不虚高",
        image=_img(state),
        items=[
            {"label": "指导价", "value": "XX.XX 万", "note": "占位"},
            {"label": "本期优惠", "value": "综合优惠 X.X 万", "note": "含厂家/门店政策"},
            {"label": "金融贴息", "value": "至高贴息 XXXX 元", "note": "限本月"},
            {"label": "赠品礼包", "value": "贴膜/脚垫/首保等", "note": "下订即享"},
        ],
    )


# ⑧ 已提车 —— 交付关怀 + 转介绍
def care_referral(state) -> dict:
    return _card(
        title="交付关怀 + 转介绍",
        subtitle="先关怀、后转介绍，不功利",
        image=_img(state),
        items=[
            {"label": "用车关怀", "value": "3 天回访 + 首保提醒", "note": "提升满意度"},
            {"label": "答疑通道", "value": "专属顾问随时在线", "note": "用车无忧"},
            {"label": "转介绍礼", "value": "老带新各得 XX(占位)", "note": "自然引出，不逼推"},
        ],
    )


def _img(state):
    """车型图文件名：优先用 state 上显式指定的 image；否则 None(前端占位)。"""
    return getattr(state, "image", None) or None


# 本文件内的桩工具注册表（与 model_comparison 的合并在 tools/__init__.py）
STUB_REGISTRY = {
    "brand_proof": brand_proof,
    "product_highlight": product_highlight,
    "finance_calc": finance_calc,
    "model_select": model_select,
    "test_drive_booking": test_drive_booking,
    "quote_offer": quote_offer,
    "care_referral": care_referral,
}
