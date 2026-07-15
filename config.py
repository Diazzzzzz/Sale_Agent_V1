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
