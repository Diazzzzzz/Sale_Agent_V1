"""工具箱统一出口：合并「车型对比(真桩)」+「其余七节点演示桩」。
引擎按名字查这个 ALL_TOOLS。接真数据时，替换对应工具函数即可，引擎不改。"""
from tools.model_comparison import REGISTRY as _COMPARE
from tools.stubs import STUB_REGISTRY as _STUBS

ALL_TOOLS = {**_COMPARE, **_STUBS}
