"""命令行演示：跑一个样例客户，走完引擎一轮 ——
感知 → 策划 → 调车型对比(桩) → 生成话术 → 停下等销售确认。

运行：
    python run_demo.py
无 API key 时自动走 mock，照样能看完整链路；
配了 DEEPSEEK_API_KEY(或火山)后，改用真模型。

想看网页聊天界面：python web.py  → 打开 http://127.0.0.1:5000
"""
from state import CustomerState
from engine import run_once
from nodes.rival_compare import PROFILE
from demo_scenarios import SCENARIOS


def main():
    sc = SCENARIOS["wang"]
    print("=" * 60)
    print("Sales Agent MVP · 引擎单轮演示")
    print(f"节点：{PROFILE.name}     工具：车型对比(桩)")
    print(f"客户：{sc['intent_car']}  比  {sc['rival_car']}")
    print("=" * 60)

    state = CustomerState(
        customer_id=sc["customer_id"],
        budget=sc["budget"],
        intent_car=sc["intent_car"],
        rival_car=sc["rival_car"],
        concerns=sc["concerns"],
    )

    state, msg = run_once(state, sc["transcript"], sc["behaviors"], PROFILE)

    print("\n" + "-" * 60)
    print("【待销售确认 · 拟发话术】\n")
    print(msg)
    print("-" * 60)
    print("\n【客户最新状态 state】")
    print(state.to_json())


if __name__ == "__main__":
    main()
