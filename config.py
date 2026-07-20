"""全局配置：LLM 供应商(DeepSeek / 火山引擎可切) + 阶段开关。"""
import os

# 两家都是 OpenAI 兼容格式，只是 base_url / 模型名不同
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "volcano": {  # 火山引擎方舟
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        # 火山用的是「推理接入点 ID」，在方舟控制台建好后填这里或用环境变量
        "model": os.getenv("VOLCANO_MODEL", "your-endpoint-id"),
        "api_key_env": "VOLCANO_API_KEY",
    },
}

# 当前用哪家：改这里，或设环境变量 LLM_PROVIDER=volcano
ACTIVE_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

# 阶段：'1'=增强人(生成后停下等销售确认，不自动触达)；'2'=端到端自动
PHASE = os.getenv("SA_PHASE", "1")

# 温度：低(0.2~0.5)=稳定、话术不乱飘；高(0.8~1.0)=更发散、每次不同
TEMPERATURE = float(os.getenv("SA_TEMPERATURE", "0.7"))

# ---- 多语言 / 目标市场 ----
# 每种语言绑定一个国家市场：生成时按该国「购车场景 + 汽车销售商务语言习惯」输出。
# 想换市场，改 country / guide 即可，引擎不用动。
LANGUAGES = {
    "zh": {"name": "中文", "flag": "🇨🇳", "country": "中国",
           "guide": "用简体中文，符合中国汽车销售顾问的沟通习惯：热情、接地气、口语化；价格用人民币（元/万）。"},
    "en": {"name": "English", "flag": "🇿🇦", "country": "South Africa",
           "guide": "Respond in English, following the car-sales business etiquette common in South Africa: "
                    "polite, professional and customer-first; quote prices in Rand (R)."},
    "ru": {"name": "Русский", "flag": "🇷🇺", "country": "Россия",
           "guide": "Отвечай на русском языке в деловом стиле продаж автомобилей, принятом в России: "
                    "вежливое обращение на «Вы», профессионально и уважительно; цены в рублях (₽)."},
    "es": {"name": "Español", "flag": "🇲🇽", "country": "México",
           "guide": "Responde en español con el estilo comercial de venta de autos usado en México: "
                    "trato de «usted», cordial y profesional; precios en pesos mexicanos (MXN $)."},
    "fr": {"name": "Français", "flag": "🇫🇷", "country": "France",
           "guide": "Réponds en français selon les usages commerciaux de la vente automobile en France : "
                    "vouvoiement, ton professionnel et courtois ; prix en euros (€)."},
}
DEFAULT_LANG = os.getenv("SA_LANG", "zh")


def lang_directive(lang: str) -> str:
    """拼一段可追加到 system prompt 末尾的『语言 + 当地商务风格』指令。中文返回空串。"""
    cfg = LANGUAGES.get(lang) or LANGUAGES[DEFAULT_LANG]
    if (lang or DEFAULT_LANG) == "zh":
        return ""
    return ("\n\n【语言与商务风格 / Language & business style】"
            f"请务必用「{cfg['name']}」回答，面向 {cfg['country']} 市场的购车场景。"
            f"{cfg['guide']} "
            f"尽量贴合 {cfg['country']} 当地汽车销售的商务沟通语言习惯与表达方式，让客户读起来像本地销售发来的。")
