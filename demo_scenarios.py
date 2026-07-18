"""八节点演示剧本：每个节点配一个客户故事，并【预置好完整的引擎五步输出】。

为什么预置？——发布/演示要稳、要好看、不烧 token：
  · 无 key(静态/mock 模式)：网页直接渲染每个剧本自带的 demo(感知/军师/工具卡/话术)，
    八条路径各不相同、100% 可控。
  · 有 key(真跑模式)：走 engine.run_engine()，感知/军师/话术由真模型现算，工具照调桩。

每个剧本结构：
  node_id     该剧本演示哪个节点(对应 nodes/ 里的档案)
  transcript  销售↔客户对话(界面画成气泡)
  image       车型图文件名(放 static/images/ 下；缺图前端自动占位)
  demo        预置的引擎五步输出：{perceive, plan, tool_results, message}
"""


def parse_dialogue(transcript: str):
    """把 '销售：xxx' / '客户：xxx' 拆成 [{who, text}]，供界面画气泡。"""
    out = []
    for raw in transcript.split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        if "：" in raw:
            who, text = raw.split("：", 1)
        elif ":" in raw:
            who, text = raw.split(":", 1)
        else:
            who, text = "客户", raw
        out.append({"who": who.strip(), "text": text.strip()})
    return out


def _generic(title, subtitle, items, image=None):
    return {"card_type": "generic", "title": title, "subtitle": subtitle,
            "image": image, "items": items, "_stub": True}


# ============================ 八节点剧本 ============================
SCENARIOS = {

    # ① 认可品牌 -------------------------------------------------------
    "brand": {
        "node_id": "brand_recognition",
        "title": "张先生 · 还信不过国产越野",
        "customer_id": "C3001",
        "intent_car": "长城坦克300",
        "rival_car": "Jeep牧马人",
        "budget": "20万左右",
        "concerns": ["品牌信任", "越野"],
        "image": "tank300.jpg",
        "behaviors": "朋友推荐来看过一次；反复问“国产越野行不行”；未留强意向。",
        "transcript": (
            "销售：张哥，上次您看的坦克300，回去还有再琢磨吗？\n"
            "客户：琢磨了，就是心里没底。这价钱我为啥不加点上牧马人？\n"
            "客户：国产越野……我怕小毛病多，也怕不保值。"
        ),
        "demo": {
            "perceive": {"hwc": "C", "node": "认可品牌",
                         "evidence": "客户拿牧马人做锚、反复质疑国产越野，尚未认可品牌，属早期冷线索"},
            "plan": {
                "goal": "打消“国产越野不如合资”的顾虑，建立对坦克品牌的初步信任",
                "actions": [{"tool": "brand_proof", "why": "客户不信任品牌，需要销量/口碑/奖项等硬事实背书"}],
                "deliverables": ["一段建立品牌信任的微信话术 + 1 张品牌实力图"],
                "timing": "冷线索，3~5 天轻触一次，不逼单",
                "talking_points": ["坦克是独立越野品牌、不是杂牌", "销量/保有量背书",
                                    "真实车主口碑", "邀到店眼见为实"],
            },
            "tool_results": [{
                "tool": "brand_proof", "why": "用硬事实背书打消顾虑",
                "result": _generic(
                    "长城坦克300 · 品牌实力背书", "用硬事实回应“国产越野行不行”",
                    [
                        {"label": "品类地位", "value": "国产硬派越野销量领先", "note": "专业越野品牌，非杂牌"},
                        {"label": "保有量", "value": "坦克品牌全球用户 XX 万", "note": "占位：填真实数字"},
                        {"label": "权威认可", "value": "多项越野车型大奖", "note": "占位：填真实奖项"},
                        {"label": "车主口碑", "value": "满意度 XX%，真实穿越作业 N 篇", "note": "占位：挂口碑素材"},
                    ], image="tank300.jpg"),
            }],
            "message": (
                "张哥，您这个顾虑我特别理解，换我买 20 万的车也会反复掂量。坦克其实不是“便宜的替代”，"
                "它是长城单独做越野的品牌——销量、保有量都摆在这，越野这块口碑是真车主一趟趟跑出来的。\n"
                "小毛病和保值您担心得对，这两点我不跟您嘴上打包票，您来店里，我把真实的车主反馈和保值数据摊给您看，"
                "再上车摸一摸，行不行您自己判断。这周末我给您留台实车？"
            ),
        },
    },

    # ② 了解产品 -------------------------------------------------------
    "product": {
        "node_id": "product_intro",
        "title": "陈女士 · 认牌了但不懂好在哪",
        "customer_id": "C3002",
        "intent_car": "长城哈弗H6",
        "rival_car": "",
        "budget": "15万内",
        "concerns": ["安全", "空间"],
        "image": "havalh6.jpg",
        "behaviors": "认可哈弗品牌；浏览过H6详情页；对具体好在哪说不上来。",
        "transcript": (
            "销售：陈姐，哈弗H6您是挺认可的，主要想多了解它哪块强？\n"
            "客户：对，牌子我放心，就是不太懂它到底好在哪。\n"
            "客户：我家有小孩，主要看重安全，还有能不能装。"
        ),
        "demo": {
            "perceive": {"hwc": "W", "node": "了解产品",
                         "evidence": "客户已认可品牌，需要围绕安全/空间讲清核心卖点，属温线索"},
            "plan": {
                "goal": "围绕客户在意的安全、空间，讲清 H6 的 2~3 个核心卖点，让她种草",
                "actions": [{"tool": "product_highlight", "why": "按在意点(安全/空间)挑亮点，避免堆参数"}],
                "deliverables": ["一段种草核心卖点的微信话术 + 1 张亮点图"],
                "timing": "温线索，2~4 天跟进一次",
                "talking_points": ["只讲安全/空间两点", "场景化(带娃出行)", "落点邀到店实车感受"],
            },
            "tool_results": [{
                "tool": "product_highlight", "why": "按在意点挑核心卖点",
                "result": _generic(
                    "长城哈弗H6 · 为您挑的核心亮点", "只讲您在意的安全 & 空间",
                    [
                        {"label": "安全", "value": "全系 6 气囊 + L2 辅助驾驶", "note": "带娃出行更放心"},
                        {"label": "空间", "value": "同级更长轴距，后排 + 后备箱能装", "note": "推车大件都塞得下"},
                    ], image="havalh6.jpg"),
            }],
            "message": (
                "陈姐，您最看重的两点我直接给您说透：一是安全，H6 全系 6 个气囊、带 L2 辅助驾驶，"
                "带娃跑长途能省不少心；二是空间，它同级里轴距算长的，后排坐得开，后备箱推车、大件都装得下。\n"
                "这些光看图没手感，您带孩子来店里，实车坐进去、后备箱塞一下，一下就清楚了。您这周哪天方便？"
            ),
        },
    },

    # ③ 明确预算 -------------------------------------------------------
    "budget": {
        "node_id": "budget_clarify",
        "title": "赵先生 · 喜欢但纠结价格",
        "customer_id": "C3003",
        "intent_car": "长城哈弗大狗",
        "rival_car": "",
        "budget": "预算模糊",
        "concerns": ["价格"],
        "image": "havaldog.jpg",
        "behaviors": "喜欢大狗的外观；一问价格就犹豫；预算没说死。",
        "transcript": (
            "销售：赵哥，大狗您是真喜欢，就是卡在价上？\n"
            "客户：对，车我满意，就是不知道落地到底多少、月供扛不扛得住。\n"
            "客户：手头预算也没完全定死。"
        ),
        "demo": {
            "perceive": {"hwc": "W", "node": "明确预算",
                         "evidence": "客户对车有意向但预算模糊、纠结价格，需把落地价/月供讲清，属温线索"},
            "plan": {
                "goal": "把落地价和月供算清、降低价格顾虑，帮客户锚定预算",
                "actions": [{"tool": "finance_calc", "why": "用落地价+分期把钱讲透明，弱化总价焦虑"}],
                "deliverables": ["一段讲清落地价/月供的微信话术 + 1 张试算卡"],
                "timing": "温线索，2~3 天跟进",
                "talking_points": ["不逼问预算", "强调月供可承受", "给几档方案让他有掌控感"],
            },
            "tool_results": [{
                "tool": "finance_calc", "why": "落地价+分期试算",
                "result": _generic(
                    "长城哈弗大狗 · 落地价 & 分期试算", "把“钱的事”讲透明，弱化总价、看月供",
                    [
                        {"label": "参考裸车价", "value": "XX.XX 万", "note": "占位：按实配置填"},
                        {"label": "落地价(含税险)", "value": "约 XX.XX 万", "note": "占位：一价清单"},
                        {"label": "首付方案", "value": "低至 30% ≈ X.X 万", "note": "门槛可再谈"},
                        {"label": "月供参考", "value": "约 X,XXX 元 / 月", "note": "分 36 期示例"},
                    ], image="havaldog.jpg"),
            }],
            "message": (
                "赵哥，车您满意就好办，价的事咱摊开算，不含糊。我按大狗给您列了个明白账：落地大概多少、"
                "首付低能到多少、分 36 期一个月大概还多少，您一眼就知道扛不扛得住。\n"
                "预算不用现在说死，您看着这个数心里先有个底。哪天来店里我把优惠和金融方案一起给您对一遍，能更省。"
            ),
        },
    },

    # ④ 明确车型 -------------------------------------------------------
    "model": {
        "node_id": "model_select",
        "title": "孙女士 · 在自家两款里挑",
        "customer_id": "C3004",
        "intent_car": "长城哈弗H6 / 哈弗大狗",
        "rival_car": "",
        "budget": "15万内",
        "concerns": ["空间", "外观"],
        "image": "havalh6.jpg",
        "behaviors": "预算已定；在 H6 和大狗之间犹豫；说不清选哪款。",
        "transcript": (
            "销售：孙姐，预算定了，就是 H6 和大狗两个拿不定？\n"
            "客户：对，H6 我觉得稳当，大狗又好看。\n"
            "客户：我要空间够、也想外观有个性，你帮我参谋下。"
        ),
        "demo": {
            "perceive": {"hwc": "W", "node": "明确车型",
                         "evidence": "客户预算已定、在本品牌两款间犹豫，需按在意点缩到 1~2 款，属温线索"},
            "plan": {
                "goal": "结合在意点(空间/外观)，在预算内帮客户缩到 1~2 款候选",
                "actions": [{"tool": "model_select", "why": "在自家车型里做有取舍的推荐，不一次推太多"}],
                "deliverables": ["一段帮客户缩范围的微信话术 + 1 张选型卡"],
                "timing": "比选期，2~3 天跟进",
                "talking_points": ["讲清两款差异", "对上空间/外观", "落点到店实车对比"],
            },
            "tool_results": [{
                "tool": "model_select", "why": "本品牌内部选型",
                "result": _generic(
                    "为您在自家车型里缩个范围", "有取舍地推，不一次推太多",
                    [
                        {"label": "候选1 · 哈弗H6", "value": "空间更均衡、家用更稳", "note": "看重能装、省心选它"},
                        {"label": "候选2 · 哈弗大狗", "value": "外观更硬派个性、辨识度高", "note": "看重颜值/态度选它"},
                        {"label": "选型建议", "value": "15 万内先锁这两款", "note": "到店实车对比最快拍板"},
                    ], image="havalh6.jpg"),
            }],
            "message": (
                "孙姐，您这俩其实各有各的好，我给您掰开说：要是更看重空间均衡、家用省心，H6 更稳；"
                "要是想外观有个性、开出去有辨识度，那就是大狗。您在意的空间两款都够，差别主要在‘稳当’还是‘个性’。\n"
                "别在图上纠结了，两台我都给您停一块儿，您来店里坐进去比一下，五分钟就有答案。周末给您留车？"
            ),
        },
    },

    # ⑤ 对比竞品 -------------------------------------------------------（保留王先生·H6 比 RAV4）
    "wang": {
        "node_id": "rival_compare",
        "title": "王先生 · 哈弗H6 比 RAV4",
        "customer_id": "C2001",
        "intent_car": "长城哈弗H6",
        "rival_car": "丰田RAV4荣放",
        "budget": "15万内",
        "concerns": ["安全", "空间", "保值"],
        "image": "havalh6.jpg",
        "behaviors": "近3天看了2次车型详情页；主动咨询过一次；未预约到店。",
        "transcript": (
            "销售：王哥您好，之前看您对哈弗H6挺感兴趣的，今天再来看看？\n"
            "客户：对，就是有点纠结。朋友让我看看丰田RAV4，说合资的保值。\n"
            "客户：我家孩子才两岁，安全我最看重，空间也得够装。\n"
            "客户：就是担心国产车小毛病多、以后不好卖、掉价快。"
        ),
        "demo": {
            "perceive": {"hwc": "H", "node": "对比竞品",
                         "evidence": "客户已在哈弗H6与RAV4之间比价，最看重安全/空间，属临近成交的热线索"},
            "plan": {
                "goal": "用有取舍、可信的对比帮客户坚定选 H6，并邀约到店试驾",
                "actions": [{"tool": "model_comparison", "why": "客户在比价，需要针对在意点的对比数据支撑"}],
                "deliverables": ["一条邀约到店试驾的微信话术 + 1 张对比卡"],
                "timing": "2 天内跟进，有互动即时响应",
                "talking_points": ["紧扣安全/空间/保值讲差异", "保值短板主动认并找补", "落点邀到店实车感受"],
            },
            "tool_results": [{
                "tool": "model_comparison", "why": "客户在比价，需要有取舍的对比",
                "result": {
                    "card_type": "comparison",
                    "our_car": "长城哈弗H6", "rival_car": "丰田RAV4荣放",
                    "image": "havalh6.jpg",
                    "summary": "同价位下，哈弗H6 在您最看重的「安全/空间」上更占优；保值这个短板可用落地价差 + 长质保找补。",
                    "dimensions": [
                        {"name": "安全", "ours": "哈弗H6：全系6气囊 + L2 辅助驾驶",
                         "rival": "RAV4：基础主动安全", "winner": "ours", "comment": "带两岁娃出行更放心"},
                        {"name": "空间", "ours": "哈弗H6：轴距更长、后备箱更能装",
                         "rival": "RAV4：够用但偏小", "winner": "ours", "comment": "推车、大件都塞得下"},
                        {"name": "保值", "ours": "哈弗H6：国产保值率近年快速提升",
                         "rival": "RAV4：合资保值率偏高", "winner": "rival",
                         "comment": "找补：算上落地价差 + 长质保，几年持有成本反而更低"},
                    ],
                    "_stub": True,
                },
            }],
            "message": (
                "王哥，您在这两款之间纠结我特别理解。我按您最在意的几点做了个实在对比：安全和空间，H6 确实更强，"
                "全系6气囊带 L2，后排和后备箱也更能装，带两岁娃出门省心。\n"
                "保值这点我不跟您绕——RAV4 是稍好，但您别只看这一项：H6 落地价本来就低一截，再加上长质保，"
                "几年下来实际持有成本不见得吃亏。\n"
                "光看参数没感觉，不如您抽空来店里，两台车我都给您备着，实车一坐一开就清楚了。这周末方便吗？"
            ),
        },
    },

    # ⑥ 到店试驾 -------------------------------------------------------
    "testdrive": {
        "node_id": "test_drive",
        "title": "李女士 · 有意向没到店",
        "customer_id": "C3006",
        "intent_car": "长城坦克300",
        "rival_car": "",
        "budget": "20万左右",
        "concerns": ["越野", "配置"],
        "image": "tank300.jpg",
        "behaviors": "线上聊了多次、意向明确；总说“最近忙”，一直没到店。",
        "transcript": (
            "销售：李姐，坦克300您是看准了，就差来试一把了。\n"
            "客户：是想去，最近实在太忙，老抽不出空。\n"
            "客户：等我有空吧，到时候再约。"
        ),
        "demo": {
            "perceive": {"hwc": "H", "node": "到店试驾",
                         "evidence": "客户意向明确但一直没到店、以‘忙’推延，属需临门一脚的热线索"},
            "plan": {
                "goal": "促成一次有具体时间的到店试驾",
                "actions": [{"tool": "test_drive_booking", "why": "给具体时段+留车+到店礼，降低到店决策成本"}],
                "deliverables": ["一段促成到店的微信话术 + 1 张试驾预约卡"],
                "timing": "热线索，快速跟进；约定后临期再提醒",
                "talking_points": ["给两三个时段二选一", "强调已留实车", "用到店礼制造理由"],
            },
            "tool_results": [{
                "tool": "test_drive_booking", "why": "促成到店试驾",
                "result": _generic(
                    "到店试驾 · 为您留车留时段", "两三个时段二选一，降低到店决策成本",
                    [
                        {"label": "试驾车型", "value": "长城坦克300", "note": "已为您备好实车"},
                        {"label": "推荐时段", "value": "本周六 10:30 / 周日 15:00", "note": "二选一即可"},
                        {"label": "门店", "value": "XX 坦克中心(占位：门店名/地址)", "note": "导航一键可达"},
                        {"label": "到店礼", "value": "试驾即赠 XX(占位)", "note": "制造到店理由"},
                    ], image="tank300.jpg"),
            }],
            "message": (
                "李姐，我懂您忙，那咱把事儿简化：不用您费神挑时间，我给您留了两个现成的——本周六上午 10:30、"
                "或者周日下午 3 点，您回我一个字母就行。实车我已经给您备好了，来了直接开。\n"
                "对了，这两天到店试驾还有个小礼(占位)，正好一块儿领。周六还是周日，您定？"
            ),
        },
    },

    # ⑦ 商务谈判 -------------------------------------------------------
    "deal": {
        "node_id": "negotiation",
        "title": "周先生 · 试驾满意开始谈价",
        "customer_id": "C3007",
        "intent_car": "长城坦克300",
        "rival_car": "",
        "budget": "20万出头",
        "concerns": ["价格", "优惠"],
        "image": "tank300.jpg",
        "behaviors": "已到店试驾、很满意；进入谈价；关注最终优惠。",
        "transcript": (
            "销售：周哥，昨天试完您挺满意，那咱就聊聊价了。\n"
            "客户：车没问题，就看你们最后能给到什么价。\n"
            "客户：优惠给到位，我今天就能定。"
        ),
        "demo": {
            "perceive": {"hwc": "H", "node": "商务谈判",
                         "evidence": "客户试驾满意、主动谈价并释放‘今天能定’信号，属临门成交的热线索"},
            "plan": {
                "goal": "给一版透明报价 + 当期限时优惠，推进今日下订",
                "actions": [{"tool": "quote_offer", "why": "分项报价+限时政策，诚意透明地推进成交"}],
                "deliverables": ["一段促成下订的微信话术 + 1 张报价单"],
                "timing": "热线索，当日响应，优惠临期提醒",
                "talking_points": ["分项列清诚意", "限时政策制造合理紧迫", "守底线也给足诚意"],
            },
            "tool_results": [{
                "tool": "quote_offer", "why": "给报价+优惠推进成交",
                "result": _generic(
                    "长城坦克300 · 本期报价单", "分项列清、限时政策，诚意透明",
                    [
                        {"label": "指导价", "value": "XX.XX 万", "note": "占位"},
                        {"label": "本期优惠", "value": "综合优惠 X.X 万", "note": "含厂家/门店政策"},
                        {"label": "金融贴息", "value": "至高贴息 XXXX 元", "note": "限本月"},
                        {"label": "赠品礼包", "value": "贴膜/脚垫/首保等", "note": "下订即享"},
                    ], image="tank300.jpg"),
            }],
            "message": (
                "周哥，痛快！我也不跟您绕弯子，直接把底摊给您：这台综合优惠能到 X.X 万，再加本月的金融贴息，"
                "还有贴膜脚垫首保这套礼包，下订就送。这价我尽力争的，诚意您能看出来。\n"
                "这个政策是本月限时的，您今天定正好赶上。要不咱现在就把手续走了？"
            ),
        },
    },

    # ⑧ 已提车 -------------------------------------------------------
    "delivered": {
        "node_id": "delivered",
        "title": "吴女士 · 已提车，做关怀+转介绍",
        "customer_id": "C3008",
        "intent_car": "长城哈弗H6",
        "rival_car": "",
        "budget": "已成交",
        "concerns": ["用车", "转介绍"],
        "image": "havalh6.jpg",
        "behaviors": "上周提的 H6；朋友圈晒了新车；用车刚上手。",
        "transcript": (
            "销售：吴姐，新车开了一周，用着还顺手吧？\n"
            "客户：挺好的，就是有些功能还没摸透。\n"
            "客户：朋友看我提了，也有两个在问呢。"
        ),
        "demo": {
            "perceive": {"hwc": "S", "node": "已提车",
                         "evidence": "客户已交付用车一周、并透露身边有人在问，属交付关怀+转介绍时机"},
            "plan": {
                "goal": "做好交付关怀提升满意度，并自然邀约转介绍",
                "actions": [{"tool": "care_referral", "why": "先关怀(用车/首保)再自然引出转介绍激励"}],
                "deliverables": ["一段关怀+转介绍的微信话术 + 1 张关怀卡"],
                "timing": "提车后 3 天回访、首保前提醒，节点式关怀",
                "talking_points": ["先真诚关怀", "答疑到位", "自然带出老带新、不逼推"],
            },
            "tool_results": [{
                "tool": "care_referral", "why": "关怀+转介绍",
                "result": _generic(
                    "交付关怀 + 转介绍", "先关怀、后转介绍，不功利",
                    [
                        {"label": "用车关怀", "value": "3 天回访 + 首保提醒", "note": "提升满意度"},
                        {"label": "答疑通道", "value": "功能不懂随时问我", "note": "用车无忧"},
                        {"label": "转介绍礼", "value": "老带新各得 XX(占位)", "note": "自然引出，不逼推"},
                    ], image="havalh6.jpg"),
            }],
            "message": (
                "吴姐，用着顺手就好！您说没摸透的功能，我整理个两分钟的小视频发您，照着点一遍就会了，"
                "首保时间到我也会提前提醒您，不用您记。\n"
                "对了，您朋友要是真有意向，直接让他报您名字来找我，我给他按您这个待遇走，"
                "而且咱俩老带新各有一份礼(占位)。您帮我引荐，我一定把人服务好，不给您丢面子。"
            ),
        },
    },
}


# 网页顶部导航用：按八节点顺序列出（依赖 nodes 的顺序）
def list_scenarios():
    """返回 [{id, title, node_id, node_name}]，按八节点旅程顺序。"""
    from nodes import NODES, BY_ID
    order = {p.node_id: i for i, p in enumerate(NODES)}
    items = [{"id": k, "title": v["title"], "node_id": v["node_id"]}
             for k, v in SCENARIOS.items()]
    items.sort(key=lambda x: order.get(x["node_id"], 99))
    for it in items:
        p = BY_ID.get(it["node_id"])
        it["node_name"] = p.name if p else it["node_id"]
    return items


def scenario_for_node(node_id: str):
    """按 node_id 找到对应剧本 id；找不到返回 None。"""
    for k, v in SCENARIOS.items():
        if v["node_id"] == node_id:
            return k
    return None
