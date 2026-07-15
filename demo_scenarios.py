"""网页聊天演示用的 mock 剧本（销售↔客户对话片段 + 场景标签）。
每个剧本自带 perceived（无 key 的 mock 模式直接用它，保证跟对话对得上）；
配了 DeepSeek key 时，感知会走真模型，不用这里的 perceived。"""


def parse_dialogue(transcript: str):
    """把 '销售：xxx' / '客户：xxx' 拆成 [{who, text}]，供界面画成气泡。"""
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


SCENARIOS = {
    "wang": {
        "title": "王先生 · 哈弗H6 比 RAV4",
        "customer_id": "C2001",
        "intent_car": "长城哈弗H6",
        "rival_car": "丰田RAV4荣放",
        "budget": "15万内",
        "concerns": ["安全", "空间", "保值"],
        "behaviors": "近3天看了2次车型详情页；主动咨询过一次；未预约到店。",
        "perceived": {"hwc": "H", "node": "对比竞品",
                      "evidence": "客户已在哈弗H6与RAV4之间比价，最看重安全/空间，属临近成交的热线索"},
        "transcript": (
            "销售：王哥您好，之前看您对哈弗H6挺感兴趣的，今天再来看看？\n"
            "客户：对，就是有点纠结。朋友让我看看丰田RAV4，说合资的保值。\n"
            "客户：我家孩子才两岁，安全我最看重，空间也得够装。\n"
            "客户：就是担心国产车小毛病多、以后不好卖、掉价快。"
        ),
    },
    "li": {
        "title": "李女士 · 坦克300 比 途观L",
        "customer_id": "C2002",
        "intent_car": "长城坦克300",
        "rival_car": "大众途观L",
        "budget": "20万左右",
        "concerns": ["配置", "空间", "油耗"],
        "behaviors": "两次到店看车；关注越野与外观；还在比价中。",
        "perceived": {"hwc": "H", "node": "对比竞品",
                      "evidence": "客户在坦克300与途观L之间摇摆，主动问差异，属热线索"},
        "transcript": (
            "销售：李姐，坦克300和途观L您还在两个里挑？\n"
            "客户：对，我喜欢坦克方正硬派，但又觉得大众牌子稳。\n"
            "客户：配置和空间我都在意，就是担心坦克油耗高、市区不好停。\n"
            "客户：你帮我说说，到底选哪个更值？"
        ),
    },
}


def list_scenarios():
    return [{"id": k, "title": v["title"]} for k, v in SCENARIOS.items()]
