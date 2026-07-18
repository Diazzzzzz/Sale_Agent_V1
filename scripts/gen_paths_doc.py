"""生成《八节点引擎通路》说明文档(HTML)。
直接从 demo_scenarios(剧本) + nodes(节点档案) 读数据渲染，
保证文档内容与代码 100% 一致。数据改了，重跑本脚本即可更新。

用法：  python scripts/gen_paths_doc.py   →  docs/八节点引擎通路.html
"""
import os
import sys
import html

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_scenarios import SCENARIOS, scenario_for_node  # noqa: E402
from nodes import NODES, get_profile                      # noqa: E402

HWC = {
    "H": ("H 热线索", "1 周内可成交", "#E5484D"),
    "W": ("W 温线索", "1~3 月考虑期", "#D8880B"),
    "C": ("C 冷线索", "3 月+/未明确", "#2563C9"),
    "O": ("O 已下订", "已下订", "#178A5A"),
    "S": ("S 已交付", "已提车交付", "#7B4DD6"),
}


def esc(s):
    return html.escape(str(s if s is not None else ""))


def render_tool(tr):
    r = tr.get("result", {})
    if r.get("card_type") == "comparison":
        rows = ""
        for d in r.get("dimensions", []):
            ours = d.get("winner") == "ours"
            tag = ('<span class="tag ok">我方占优</span>' if ours
                   else '<span class="tag fb">对手更强</span>')
            cmt = f'<div class="cmt">{"找补：" if not ours else ""}{esc(d.get("comment"))}</div>'
            rows += (f'<tr><td class="dn">{esc(d.get("name"))} {tag}</td>'
                     f'<td class="{"win" if ours else ""}">{esc(d.get("ours"))}</td>'
                     f'<td class="{"" if ours else "weak"}">{esc(d.get("rival"))}{cmt}</td></tr>')
        return (f'<div class="tool">'
                f'<div class="tt">🔧 车型对比 · {esc(r.get("our_car"))} vs {esc(r.get("rival_car"))}'
                f'<span class="ex">示例数据</span></div>'
                f'<div class="ts">{esc(r.get("summary"))}</div>'
                f'<table class="cmp"><tr><th>维度</th><th>我方</th><th>竞品</th></tr>{rows}</table>'
                f'</div>')
    # generic
    items = ""
    for it in r.get("items", []):
        note = f' <span class="nt">· {esc(it.get("note"))}</span>' if it.get("note") else ""
        items += (f'<div class="gi"><span class="gk">{esc(it.get("label"))}</span>'
                  f'<span class="gv"><b>{esc(it.get("value"))}</b>{note}</span></div>')
    img = (f'<div class="imgtag">配图：{esc(r.get("image"))}</div>' if r.get("image") else "")
    return (f'<div class="tool">'
            f'<div class="tt">🔧 {esc(r.get("title"))}<span class="ex">示例数据</span></div>'
            f'<div class="ts">{esc(r.get("subtitle"))}</div>{img}{items}</div>')


def chips(lst, cls="chip"):
    return "".join(f'<span class="{cls}">{esc(x)}</span>' for x in (lst or []))


def render_node(idx, p, sid, sc):
    d = sc["demo"]
    per, plan = d["perceive"], d["plan"]
    hlbl, hdesc, hcol = HWC.get(per["hwc"], (per["hwc"], "", "#888"))
    tools = "".join(
        f'<span class="chip tool">🔧 {esc(a.get("tool"))}'
        f'{" · " + esc(a.get("why")) if a.get("why") else ""}</span>'
        for a in plan.get("actions", [])) or '<span class="dim">本轮不调用工具</span>'
    tags = ""
    for k, v in [("客户", sc["title"]), ("意向车", sc["intent_car"]),
                 ("竞品", sc.get("rival_car")), ("预算", sc["budget"]),
                 ("在意", "、".join(sc["concerns"]))]:
        if v:
            tags += f'<span class="t"><b>{k}</b> {esc(v)}</span>'
    tools_cards = "".join(render_tool(tr) for tr in d["tool_results"]) \
        or '<div class="dim">本节点本轮无工具调用（感知 → 军师 → 直接生成话术）</div>'
    msg = esc(d["message"]).replace("\n", "<br>")

    return f'''
<section class="node" id="n{idx}">
  <div class="nhd"><span class="nn">{idx}</span>
    <div><div class="ntitle">{esc(p.name)}</div>
    <div class="nsub">{esc(sc["title"])}</div></div>
  </div>
  <div class="tags">{tags}</div>

  <div class="step"><div class="sl">① 状态感知 · 客户分级</div>
    <div><span class="hwc" style="background:{hcol}">{esc(hlbl)}</span>
      <span class="nodechip">{esc(per["node"])}</span>
      <span class="dim">（{esc(hdesc)}）</span></div>
    <div class="ev">依据：{esc(per["evidence"])}</div>
  </div>

  <div class="mid">选中节点档案 · <b>{esc(p.name)}</b> ｜ 目标：{esc(p.goal)} ｜ 时机：{esc(p.timing)}</div>

  <div class="step"><div class="sl">② 策略制定（决策本轮引擎动作，只决策不写话术）</div>
    <div class="row"><span class="k">目标</span><span class="v"><b>{esc(plan.get("goal"))}</b></span></div>
    <div class="row"><span class="k">工具选择</span><span class="v">{tools}</span></div>
    <div class="row"><span class="k">生成物</span><span class="v">{chips(plan.get("deliverables"), "chip out")}</span></div>
    <div class="row"><span class="k">时机</span><span class="v dim">{esc(plan.get("timing"))}</span></div>
    <div class="row"><span class="k">要点</span><span class="v">{chips(plan.get("talking_points"))}</span></div>
  </div>

  <div class="step"><div class="sl">③ 执行 · 调用工具agent</div>{tools_cards}</div>

  <div class="step"><div class="sl">④ 执行 · 生成话术（这一步才动笔）</div>
    <div class="talk">{msg}</div>
  </div>

  <div class="step"><div class="sl">⑤ 回写 · 待销售确认</div>
    <div>阶段一（增强人）：话术不自动发，写入 <code>pending_action</code>（渠道：微信），
      <b>销售确认才触达</b>；<code>history</code> 记一笔本轮。</div>
    <div class="adv">达成后推进 → <b>{esc(p.advance_to)}</b></div>
  </div>
</section>'''


def main():
    toc = "".join(
        f'<a href="#n{i}"><span>{i}</span>{esc(p.name)}</a>'
        for i, p in enumerate(NODES, 1))
    sections = ""
    for i, p in enumerate(NODES, 1):
        sid = scenario_for_node(p.node_id)
        sections += render_node(i, p, sid, SCENARIOS[sid])

    doc = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OmniSA · Sales Agent 八节点引擎通路</title>
<style>
  :root{{--bg:#F4F7FB;--ink:#0F1B2D;--soft:#3C4A60;--muted:#6B7A93;--line:#E1E8F1;
    --accent:#1E5AD6;--accent-soft:#EAF1FD;--sans:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:var(--sans);background:var(--bg);color:var(--ink);line-height:1.65}}
  .wrap{{max-width:880px;margin:0 auto;padding:28px 18px 70px}}
  h1{{font-size:23px;margin-bottom:6px}}
  .lead{{color:var(--muted);font-size:14px;margin-bottom:18px}}
  .overview{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:20px}}
  .overview h2{{font-size:15px;color:var(--accent);margin-bottom:8px}}
  .flow{{font-size:13.5px;color:var(--soft);line-height:2}}
  .flow code{{background:var(--accent-soft);color:var(--accent);border-radius:5px;padding:1px 6px;font-size:12.5px}}
  .toc{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px}}
  .toc a{{display:flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);
    border-radius:20px;padding:6px 13px;text-decoration:none;color:var(--soft);font-size:13px}}
  .toc a span{{width:19px;height:19px;border-radius:50%;background:var(--accent);color:#fff;
    display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}}

  .node{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px;margin-bottom:22px}}
  .nhd{{display:flex;align-items:center;gap:12px;margin-bottom:14px}}
  .nn{{width:34px;height:34px;border-radius:9px;background:var(--accent);color:#fff;
    display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:800;flex:0 0 auto}}
  .ntitle{{font-size:18px;font-weight:800}}
  .nsub{{font-size:13px;color:var(--muted)}}
  .tags{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}}
  .tags .t{{font-size:12.5px;background:var(--accent-soft);border:1px solid #cfe0fb;border-radius:20px;
    padding:4px 11px;color:var(--soft)}}
  .tags .t b{{color:var(--accent)}}

  .step{{border-left:3px solid var(--accent-soft);padding:2px 0 4px 16px;margin:0 0 14px 6px}}
  .sl{{font-size:15.5px;font-weight:800;color:var(--accent);margin-bottom:9px}}
  .hwc{{font-weight:800;color:#fff;border-radius:6px;padding:1px 9px;font-size:12.5px;margin-right:6px}}
  .nodechip{{font-weight:700;color:var(--accent);background:var(--accent-soft);border-radius:6px;padding:1px 9px;font-size:12.5px}}
  .ev{{color:var(--muted);font-size:12.5px;margin-top:8px}}
  .dim{{color:var(--muted);font-size:12.5px}}
  .mid{{background:#f7f9fc;border:1px dashed var(--line);border-radius:10px;padding:9px 13px;
    font-size:12.5px;color:var(--soft);margin:0 0 14px 6px}}
  .mid b{{color:var(--accent)}}
  .row{{display:flex;gap:8px;margin-bottom:7px;align-items:baseline}}
  .row .k{{flex:0 0 62px;font-size:11.5px;color:var(--muted);font-weight:700}}
  .row .v{{flex:1}}
  .chip{{display:inline-block;font-size:11.5px;background:var(--accent-soft);color:var(--accent);
    border-radius:20px;padding:3px 10px;margin:2px 4px 2px 0;font-weight:600}}
  .chip.out{{background:#eef7ee;color:#2e7d32}}
  .chip.tool{{background:#fff}}

  .tool{{border:1px solid var(--line);border-radius:12px;padding:12px;margin-top:6px}}
  .tt{{font-weight:800;font-size:13.5px}}
  .ex{{font-size:10.5px;color:#b26a00;background:#fff4e5;border-radius:5px;padding:1px 7px;margin-left:7px;font-weight:700}}
  .ts{{font-size:12.5px;color:var(--muted);margin:3px 0 9px}}
  .imgtag{{font-size:11.5px;color:#8a5a12;background:#fff7ea;border-radius:5px;padding:2px 8px;display:inline-block;margin-bottom:8px}}
  .gi{{display:flex;gap:8px;font-size:13px;margin-bottom:5px}}
  .gi .gk{{flex:0 0 84px;color:var(--muted)}}
  .gi .gv b{{color:var(--ink)}}
  .gi .nt{{color:#c77700;font-size:11.5px}}
  .cmp{{width:100%;border-collapse:collapse;margin-top:4px;font-size:12.5px}}
  .cmp th,.cmp td{{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}}
  .cmp th{{background:#f7f9fc}}
  .cmp .win{{background:var(--accent-soft)}}
  .cmp .weak{{background:#fffdf7}}
  .cmp .dn{{font-weight:700;white-space:nowrap}}
  .cmp .cmt{{color:var(--muted);font-size:11.5px;margin-top:4px}}
  .tag{{font-size:10px;font-weight:700;padding:1px 6px;border-radius:20px;margin-left:4px}}
  .tag.ok{{background:var(--accent);color:#fff}} .tag.fb{{background:#f6e2c2;color:#8a5a12}}

  .talk{{background:#fbfaf6;border:1px dashed #e3d9b8;border-radius:12px;padding:13px;font-size:13.5px;line-height:1.85}}
  code{{background:#eef1f6;border-radius:5px;padding:1px 6px;font-size:12px;color:#445}}
  .adv{{margin-top:9px;font-size:13px;color:var(--accent)}}
  .foot{{text-align:center;color:var(--muted);font-size:12px;margin-top:10px}}
</style></head>
<body><div class="wrap">
  <h1>🤖 OmniSA · Sales Agent 八节点引擎通路</h1>
  <p class="lead">同一个引擎，跑八个节点 —— 每个节点从「感知」到「回写」的完整通路。数据取自演示剧本，与代码一致。</p>

  <div class="overview">
    <h2>引擎五步（八节点共用同一套）</h2>
    <div class="flow">
      <b>①感知</b> 读对话/行为 → 判 HWC 热度 + 在哪个节点 →
      <b>选档案</b>（该节点的目标/可调工具/时机）→
      <b>②军师</b> 只决策：定目标、选工具、定生成物（不写话术）→
      <b>③执行·调用</b> 按军师点名调工具，产出卡 →
      <b>④执行·生成</b> 照卡+要点写客户话术（这才动笔）→
      <b>⑤回写</b> 阶段一挂起 <code>pending_action</code>，销售确认才发。<br>
      八节点通路完全一样，差异只在「选档案」换了哪份档案、②军师据此选的工具不同。
    </div>
  </div>

  <div class="toc">{toc}</div>
  {sections}
  <p class="foot">由 scripts/gen_paths_doc.py 从代码自动生成 · 卡片内数字为示例数据，接真实内容库/画像库后替换</p>
</div></body></html>'''

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "八节点引擎通路.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("已生成：", out, f"({len(doc)} 字节)")


if __name__ == "__main__":
    main()
