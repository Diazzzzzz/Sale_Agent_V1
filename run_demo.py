"""演示：跑一个样例客户，走完引擎一轮 ——
感知 → 策划 → 调车型对比(桩) → 生成话术 → 停下等销售确认。

运行：
    python run_demo.py
无 API key 时自动走 mock，照样能看完整链路；
配了 DEEPSEEK_API_KEY(或火山)后，改用真模型。"""
from state import CustomerState
from engine import run_once
from nodes.budget_to_model import PROFILE

CONVERSATION = """客户：你们那款SUV我看了，预算我大概就20万左右吧。
销售：好的，20万这个预算选择挺多的。
客户：主要家里用，平时接送孩子、周末偶尔出去玩。空间和油耗我比较在意，具体哪款还没想好。"""

BEHAVIORS = "近3天看了2次车型详情页；主动咨询过一次；未预约到店。"


def main():
    print("=" * 60)
    print("Sales Agent MVP · 引擎单轮演示")
    print("节点：明确预算 → 明确车型     工具：车型对比(桩)")
    print("=" * 60)

    state = CustomerState(
        customer_id="C10086",
        budget="20万",
        concerns=["空间", "油耗"],
    )

    state, msg = run_once(state, CONVERSATION, BEHAVIORS, PROFILE)

    print("\n" + "-" * 60)
    print("【待销售确认 · 拟发话术】\n")
    print(msg)
    print("-" * 60)
    print("\n【客户最新状态 state】")
    print(state.to_json())


if __name__ == "__main__":
    main()
