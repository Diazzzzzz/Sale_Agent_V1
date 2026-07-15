# Sale_Agent_V1 · OmniSA Sales Agent MVP

汽车出海 SCRM 产品 **OmniSA** 的 Sales Agent 最小可跑原型。
本 MVP 用来验证一件事：**「1 个引擎 + N 份节点档案 + 工具 + 人工确认闸」这套架构成立** ——
证明后，剩下的节点就是「填档案」，架构风险清零。

## 核心架构

```
循环(loop) · 引擎五步：感知 → 策划 → 生成 → 执行 → 回写
      +  状态/记忆(state)   ← Sales Agent 的"人"
      +  节点档案(profile)  ← 底座上长出的"分支"，是配置不是代码
      +  工具箱(tools)      ← 车型对比等子能力
      +  人工确认闸(阶段一) ← 生成后停下，销售确认才触达
```

- **引擎是共同底座**，只写一次（[engine.py](engine.py)）。
- **每个节点只是一份档案**（[nodes/](nodes/)），差异 = 目标 / 话术指引 / 可调工具 / 时机。
  扩到 10 个节点 = 加 2 份档案，**不改引擎代码**。
- **状态感知**（[perceive.py](perceive.py)）判 HWC 热度 + 八节点位置，是引擎第一步，也可独立跑。
- **LLM 层**（[llm.py](llm.py)）封装，DeepSeek / 火山引擎一键切换。

## 目录

| 文件 | 作用 |
|---|---|
| `config.py` | 供应商 / 阶段开关 |
| `llm.py` | LLM 调用层（DeepSeek/火山可切；无 key 自动 mock） |
| `state.py` | 客户工作态（薄契约，画像库定稿后插进来） |
| `perceive.py` | 状态感知：对话/行为 → HWC + 节点 |
| `engine.py` | 引擎五步循环（共同底座） |
| `nodes/budget_to_model.py` | 节点档案 #1：明确预算 → 明确车型 |
| `tools/model_comparison.py` | 车型对比工具（桩，任务2替换成真的） |
| `run_demo.py` | 跑一个客户案例看完整链路 |

## 运行

```bash
# 1) 无 key 也能跑（走 mock，看流程）
python run_demo.py

# 2) 接真模型
pip install -r requirements.txt
cp .env.example .env        # 填入 DEEPSEEK_API_KEY，或 LLM_PROVIDER=volcano + VOLCANO_*
# 让 .env 生效（任选）：export $(grep -v '^#' .env | xargs)
python run_demo.py
```

演示会：喂一段客户对话 → 感知判「温线索 / 明确预算节点」→ 引擎决定推车型对比 →
调 `model_comparison` 工具 → 生成一条微信话术 → **停在「待销售确认」**（阶段一不真发）。

## 路线图

- [x] 状态感知 + 引擎骨架 + 1 节点 + 1 工具桩 + 人工闸（本 MVP）
- [ ] 车型对比工具接真实内容库（**任务2**）
- [ ] 补齐其余 7 个节点档案
- [ ] 客户工作态对接画像库正式 schema
- [ ] 阶段二：端到端自动触达通道
