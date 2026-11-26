#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator for the Chinese AI engineering interview bank.

Design language borrowed from aiengineeringfromscratch.com/interviews:
blueprint blue, paper dot-grid, hard offset shadows, pixel display type,
monospace metadata, collapsible answers.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
CORPUS = json.loads((ROOT / "src" / "corpus.json").read_text(encoding="utf-8"))
KNOWLEDGE: dict[str, dict] = {}
for f in sorted((ROOT / "knowledge").glob("*.json")):
    KNOWLEDGE.update(json.loads(f.read_text(encoding="utf-8")))

SITE_NAME = "AI 工程面试题库"
SITE_TAG = "中文版 · 按公司分类"
REPO = "https://github.com/ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn"
UPSTREAM = "https://github.com/pallavi-shekhar/ai-engineering-interview-questions-company-wise"
SCHOOL = "https://outcomeschool.com/program/ai-and-machine-learning"
BUILD_DATE = "2026-11-06"

# --------------------------------------------------------------------------- meta

TOPIC_META = [
    ("t0", "LLM 内部机制与架构", "注意力、KV 缓存、位置编码、MoE、缩放定律——所有后续问题的地基。"),
    ("t1", "推理服务与 GPU 性能", "prefill/decode、连续批处理、PagedAttention、量化与并行策略。"),
    ("t2", "RAG 与检索", "分块、混合检索、重排序、索引新鲜度与权限感知检索。"),
    ("t3", "Agent 与工具调用", "ReAct、工具设计、MCP、记忆、终止条件与人在环路。"),
    ("t4", "微调后训练与对齐", "RLHF、DPO、GRPO、LoRA/QLoRA、灾难性遗忘与蒸馏。"),
    ("t5", "评估与可观测性", "LLM-as-judge、回归门禁、幻觉度量、基准污染与在线实验。"),
    ("t6", "安全安保与负责任 AI", "提示注入、越狱、护栏、Constitutional AI 与红队。"),
    ("t7", "多模态语音与音频 AI", "视觉 token、实时语音延迟预算、打断、说话人分离。"),
    ("t8", "AI 系统设计", "企业 RAG、代码助手、客服 agent、Text-to-SQL、LLM 网关。"),
    ("t9", "编码与数据结构", "手写注意力、KV 缓存、采样、LRU、限流器、SSE 解析。"),
]

CATEGORY_META = {
    "前沿 AI 实验室": "模型能力的定义者，面试最看重对底层机制的第一性理解与手写实现。",
    "大型科技公司的 AI 组织": "平台与产品规模大，系统设计、可靠性与跨团队协作占比高。",
    "中国互联网公司": "业务场景密集，工程落地、推理成本与中文/多模态数据是高频考点。",
    "AI 基础设施与平台公司": "卖算力与工具，问题集中在推理性能、分布式与开发者体验。",
    "AI 原生应用公司": "产品迭代快，考察端到端系统设计、评估闭环与成本控制。",
    "前向部署与企业级 AI": "直接面对客户，方案设计、权限合规与交付能力比模型细节更重要。",
}

COMPANY_IDS = {
    "Anthropic": "anthropic",
    "OpenAI": "openai",
    "Google DeepMind and Google AI": "google-deepmind",
    "Meta (Superintelligence Labs, FAIR, Llama)": "meta",
    "xAI": "xai",
    "Mistral AI": "mistral",
    "Cohere": "cohere",
    "DeepSeek": "deepseek",
    "Moonshot AI (Kimi)": "moonshot",
    "Zhipu AI (GLM)": "zhipu",
    "Alibaba (Qwen)": "alibaba-qwen",
    "Sarvam AI": "sarvam",
    "Microsoft": "microsoft",
    "Amazon (AWS)": "amazon",
    "Apple": "apple",
    "NVIDIA": "nvidia",
    "Tesla": "tesla",
    "消费者级 ML 公司 (Uber, Netflix, LinkedIn, Airbnb, Pinterest, Spotify)": "consumer-ml",
    "字节跳动": "bytedance",
    "腾讯": "tencent",
    "阿里巴巴(淘天、阿里云)": "alibaba-taotian",
    "滴滴": "didi",
    "京东": "jd",
    "美团": "meituan",
    "Databricks": "databricks",
    "Groq": "groq",
    "Together AI": "together",
    "Hugging Face": "huggingface",
    "Scale AI": "scale",
    "Perplexity": "perplexity",
    "Cursor (Anysphere)": "cursor",
    "Cognition (Devin, Windsurf)": "cognition",
    "Sierra": "sierra",
    "Harvey": "harvey",
    "Glean": "glean",
    "Character.AI": "character-ai",
    "ElevenLabs": "elevenlabs",
    "Abridge": "abridge",
    "Figure AI": "figure",
    "Waymo": "waymo",
    "Palantir": "palantir",
}

SHORT_NAME = {
    "消费者级 ML 公司 (Uber, Netflix, LinkedIn, Airbnb, Pinterest, Spotify)": "消费者级 ML 公司",
    "Meta (Superintelligence Labs, FAIR, Llama)": "Meta",
    "Google DeepMind and Google AI": "Google DeepMind",
    "Alibaba (Qwen)": "Alibaba (Qwen)",
    "Moonshot AI (Kimi)": "Moonshot AI (Kimi)",
    "Zhipu AI (GLM)": "Zhipu AI (GLM)",
    "Amazon (AWS)": "Amazon (AWS)",
    "Cursor (Anysphere)": "Cursor",
    "Cognition (Devin, Windsurf)": "Cognition",
}

CATEGORY_ORDER = list(CATEGORY_META.keys())

# --------------------------------------------------------------------------- helpers


TERM_FIXES = (
    ("消费者级 ML 公司", "消费级 ML 公司"),
    ("前向外派", "前向部署"),
    ("买到了什么", "换来了什么"),
    ("形状高度一致", "结构高度一致"),
    ("有实质内容、会被刷", "有实质内容、会刷人"),
    ("约五轮的线上 onsite", "约五轮的线上现场面试（virtual onsite）"),
    ("hiring manager", "招聘经理"),
    ("serving 多种基础模型", "提供多种基础模型服务"),
)


def fix_terms(s: str) -> str:
    for a, b in TERM_FIXES:
        s = s.replace(a, b)
    return s


def clip(s: str, n: int) -> str:
    """按标点/括号边界截断，避免半个括号或半句话。"""
    if len(s) <= n:
        return s
    cut = s[:n]
    for i in range(len(cut) - 1, max(0, len(cut) - 16), -1):
        if cut[i] in "，。；：、？！)）】」":
            cut = cut[: i + 1]
            break
    for op, cl in (("(", ")"), ("（", "）"), ("【", "】")):
        if cut.count(op) > cut.count(cl):
            cut = cut[: cut.rfind(op)]
    return cut.rstrip("，、；：·") + "…"


def esc(s: str) -> str:
    return html.escape(fix_terms(s), quote=True)


CJK = "\u4e00-\u9fff\u3000-\u303f\uff00-\uffef"


def zh(s: str) -> str:
    """中文排版：术语统一 + 中文语境里的半角标点换全角。"""
    s = fix_terms(s)
    cjk = CJK
    left_any = r"[)）%”0-9A-Za-z]"
    for half, full in ((",", "，"), (":", "："), (";", "；")):
        # 左侧中文，右侧接中文/数字/引号
        s = re.sub(r"(?<=[" + cjk + r"])\s*" + re.escape(half) + r"\s*(?=[" + cjk + r"0-9A-Za-z“])", full, s)
        # 左侧是括号/百分号/字母数字，右侧接中文
        s = re.sub(r"(?<=" + left_any + r")\s*" + re.escape(half) + r"\s*(?=[" + cjk + r"])", full, s)
    s = re.sub(r"(?<=[" + cjk + r")）”])\?", "？", s)
    s = re.sub(r"(?<=[" + cjk + r"0-9A-Za-z])\?(?=\s|$)", "？", s)
    s = re.sub(r"(?<=[0-9A-Za-z])\?(?=[" + cjk + r"])", "？", s)
    s = re.sub(r"(?<=[" + cjk + r"])!(?=[" + cjk + r"”])", "！", s)
    return s


def inline(s: str) -> str:
    """中文标点归一 + HTML 转义，再允许 `code` 与 **bold**。"""
    out = esc(zh(s))
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


TOPIC_BY_ANCHOR = {name.lower().replace(" ", "-"): tid for tid, name, _ in TOPIC_META}


def inline_with_links(text: str, root: str) -> str:
    """渲染带 markdown 链接的说明文字（公司页的“另外还要准备”）。"""
    links = []

    def stash(m):
        links.append((m.group(1), m.group(2)))
        return f"\x00{len(links) - 1}\x00"

    stashed = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash, text)
    out = inline(stashed)
    for i, (label, href) in enumerate(links):
        url = None
        if href.startswith("#"):
            anchor = href[1:]
            if anchor == "跨公司通用面试题":
                url = f"{root}index.html"
            else:
                tid = TOPIC_BY_ANCHOR.get(anchor)
                if tid:
                    url = f"{root}topics/{tid}.html"
        else:
            url = href
        rendered = f'<a href="{esc(url)}">{inline(label)}</a>' if url else inline(label)
        out = out.replace(f"\x00{i}\x00", rendered)
    return out


def slug(text: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", text.lower()).strip("-")


def domain_label(url: str) -> str:
    m = re.match(r"https?://([^/]+)/", url)
    if not m:
        return "链接"
    host = m.group(1).replace("www.", "")
    return {
        "outcomeschool.com": "Outcome School",
        "outcomeschool.substack.com": "Substack",
        "youtube.com": "YouTube",
        "linkedin.com": "LinkedIn",
    }.get(host, host)


def num(n: int) -> str:
    return f"{n:02d}"


# --------------------------------------------------------------------------- layout

HEAD = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/fonts/fonts.css">
<link rel="stylesheet" href="{root}assets/site.css">
<script>(function(){{var r=document.documentElement,s='';try{{s=localStorage.getItem('theme')||'';}}catch(_){{}}
r.setAttribute('data-theme',s||(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));}})();</script>
</head>
<body>
<a class="skip-link" href="#main">跳到主要内容</a>
{header}
"""

HEADER = """<header class="site-header"><div class="header-inner">
<a href="{root}index.html" class="logo"><span class="logo-icon" aria-hidden="true"></span> AI / 面试题库</a>
<nav class="header-nav" aria-label="站点导航">
<a href="{root}index.html"{cur_home}>目录</a>
<a href="{root}companies.html"{cur_companies}>公司</a>
<a href="{root}search.html"{cur_search}>搜索</a>
<a href="{root}labs.html"{cur_labs}>可视化</a>
<a href="{root}about.html"{cur_about}>关于</a>
<a href="{repo}" class="header-github" target="_blank" rel="noopener">GitHub <span aria-hidden="true">↗</span></a>
<button class="theme-toggle" id="themeToggle" aria-label="切换主题" type="button"><span id="themeIcon">N</span></button>
</nav></div></header>
"""

FOOTER = """<footer class="iv-site-foot">
<nav class="footer-links" aria-label="页脚">
<a href="{root}index.html">目录</a>
<a href="{root}companies.html">公司</a>
<a href="{root}search.html">搜索</a>
<a href="{root}about.html">关于</a>
<a href="{repo}" target="_blank" rel="noopener">题目来源仓库</a>
<a href="{upstream}" target="_blank" rel="noopener">英文原版</a>
</nav>
<p>{site} · {tag} · 题目整理自公开面经，答案链接指向原文；答题要点为本站整理，非官方标准答案。</p>
<p>构建于 {date} · 静态站点，无追踪脚本。</p>
</footer>
<script src="{root}assets/site.js" defer></script>
</body>
</html>
"""


def header_html(root: str, cur: str = "") -> str:
    keys = {"home": "cur_home", "companies": "cur_companies", "search": "cur_search", "labs": "cur_labs", "about": "cur_about"}
    marks = {v: "" for v in keys.values()}
    if cur in keys:
        marks[keys[cur]] = ' aria-current="page"'
    return HEADER.format(root=root, repo=REPO, **marks)


def page(title: str, desc: str, root: str, body: str, cur: str = "", extra_head: str = "") -> str:
    head = HEAD.format(title=esc(title), desc=esc(desc), root=root, header=header_html(root, cur))
    head = head.replace("</head>", extra_head + "</head>")
    foot = FOOTER.format(root=root, repo=REPO, upstream=UPSTREAM, site=SITE_NAME, tag=SITE_TAG, date=BUILD_DATE)
    return head + body + foot


# --------------------------------------------------------------------------- model

class Question:
    def __init__(self, q, tid, tname, idx):
        self.text = q["text"]
        self.raw = q["raw"]
        self.answers = q["answers"]
        self.companies = q["companies"]
        self.topic_id = tid
        self.topic_name = tname
        self.id = f"{tid}q{idx}"
        self.know = KNOWLEDGE.get(self.id)
        self.links_converted = self._links()

    def _links(self):
        # answers that are bare URLs inside question text are not present; keep answers only
        return self.answers


TOPICS = []
Q_BY_ID = {}
for ti, (tid, tname, tdesc) in enumerate(TOPIC_META):
    t = next(x for x in CORPUS["cross_topics"] if x["name"] == tname)
    qs = [Question(q, tid, tname, qi) for qi, q in enumerate(t["questions"])]
    TOPICS.append({"id": tid, "name": tname, "desc": tdesc, "questions": qs, "color": f"var(--t{ti})"})
    for q in qs:
        Q_BY_ID[q.id] = q

COMPANIES = []
for c in CORPUS["companies"]:
    cid = COMPANY_IDS[c["name"]]
    nq = sum(len(s["questions"]) for s in c["sections"])
    COMPANIES.append({
        "id": cid,
        "name": c["name"],
        "short": SHORT_NAME.get(c["name"], c["name"]),
        "category": c["category"],
        "roles": c["roles"],
        "process": c["process"],
        "prepare": c["prepare"],
        "sections": c["sections"],
        "nq": nq,
        "ntopics": len(c["sections"]),
    })
C_BY_ID = {c["id"]: c for c in COMPANIES}
C_NAME_TO_ID = {c["name"]: c["id"] for c in COMPANIES}

# alias used by cross-company "出现于" chips
ALIASES = {
    "Anthropic": "anthropic", "OpenAI": "openai", "Google DeepMind": "google-deepmind",
    "Meta": "meta", "xAI": "xai", "Mistral AI": "mistral", "Cohere": "cohere",
    "DeepSeek": "deepseek", "Moonshot AI": "moonshot", "Zhipu AI": "zhipu",
    "Alibaba": "alibaba-qwen", "Sarvam AI": "sarvam", "Microsoft": "microsoft",
    "Amazon": "amazon", "Apple": "apple", "NVIDIA": "nvidia", "Tesla": "tesla",
    "消费者级 ML 公司": "consumer-ml", "字节跳动": "bytedance", "腾讯": "tencent",
    "阿里巴巴(淘天、阿里云)": "alibaba-taotian", "滴滴": "didi", "京东": "jd",
    "美团": "meituan", "Databricks": "databricks", "Groq": "groq",
    "Together AI": "together", "Hugging Face": "huggingface", "Scale AI": "scale",
    "Perplexity": "perplexity", "Cursor": "cursor", "Cognition": "cognition",
    "Sierra": "sierra", "Harvey": "harvey", "Glean": "glean",
    "Character.AI": "character-ai", "ElevenLabs": "elevenlabs", "Abridge": "abridge",
    "Figure AI": "figure", "Waymo": "waymo", "Palantir": "palantir",
}


def company_id(name: str) -> str | None:
    if name in C_NAME_TO_ID:
        return C_NAME_TO_ID[name]
    return ALIASES.get(name)


def company_link(root: str, name: str, cls: str = "iv-tag") -> str:
    cid = company_id(name)
    label = SHORT_NAME.get(name, name)
    if not cid:
        return f'<span class="{cls}">{esc(label)}</span>'
    return f'<a class="{cls}" href="{root}companies/{cid}.html">{esc(label)}</a>'


def topic_link(root: str, t: dict, cls: str = "iv-tag") -> str:
    return f'<a class="{cls}" href="{root}topics/{t["id"]}.html">{esc(t["name"])}</a>'


# cross questions tagged for this company
CROSS_FOR_COMPANY: dict[str, list[Question]] = {c["id"]: [] for c in COMPANIES}
for t in TOPICS:
    for q in t["questions"]:
        for cn in q.companies:
            cid = company_id(cn["name"])
            if cid and q not in CROSS_FOR_COMPANY[cid]:
                CROSS_FOR_COMPANY[cid].append(q)

TOTAL_Q = sum(len(t["questions"]) for t in TOPICS) + sum(c["nq"] for c in COMPANIES)
TOTAL_ANSWERS = (sum(1 for t in TOPICS for q in t["questions"] if q.answers)
                 + sum(1 for c in COMPANIES for s in c["sections"] for q in s["questions"] if q["answers"]))

# --------------------------------------------------------------------------- components


def stats_box(companies=TOTAL_Q) -> str:
    return f"""<dl class="iv-stats">
<div><dt>公司</dt><dd>{len(COMPANIES)}</dd></div>
<div><dt>题目</dt><dd>{TOTAL_Q}</dd></div>
<div><dt>主题</dt><dd>{len(TOPICS)}</dd></div>
<div><dt>附原文答案</dt><dd>{TOTAL_ANSWERS}</dd></div>
</dl>"""


def answer_details(q: Question, root: str) -> str:
    k = q.know
    if not k:
        return ""
    points = "".join(f"<li>{inline(p)}</li>" for p in k.get("points", []))
    formula = k.get("formula")
    fblock = f"<pre><code>{esc(formula)}</code></pre>" if formula else ""
    wrong = ""
    if k.get("wrong"):
        items = "".join(
            f'<li><p class="iv-wrong-a">{inline(w)}</p></li>' for w in k["wrong"]
        )
        wrong = f'<details class="iv-answer iv-answer-small"><summary>常见错误说法</summary><div class="iv-answer-body"><ul class="iv-wrong">{items}</ul></div></details>'
    links = " · ".join(
        f'<a href="{esc(a["url"])}" target="_blank" rel="noopener">{inline(a["label"])}</a>' for a in q.answers
    )
    src = f'<p class="q-src">原文答案：{links}</p>' if links else ""
    return f"""<details class="q-answer"><summary>本站答题要点 + 原文答案</summary>
<div class="q-answer-body"><p>{inline(k['short'])}</p><ul>{points}</ul>{fblock}{src}</div></details>
{wrong}"""


def company_card(root: str, c: dict, group_color: str) -> str:
    tindex = {name: i for i, (_, name, _) in enumerate(TOPIC_META)}
    segs = "".join(
        f'<span class="iv-mix-seg" data-topic="{tindex.get(s["name"], 0)}" style="flex-grow:{len(s["questions"])}" title="{esc(s["name"])}"></span>'
        for s in c["sections"]
    )
    topics = "、".join(s["name"] for s in c["sections"][:3])
    return f"""<li class="iv-card" data-filter-item data-search="{esc(c['name'])} {esc(c['roles'])} {esc(topics)}" data-cat="{esc(c['category'])}">
<div class="iv-card-top"><span class="iv-card-count">{c['nq']} 道题</span><span>{c['ntopics']} 个板块</span></div>
<h3 class="iv-card-name"><a href="{root}companies/{c['id']}.html">{esc(c['short'])}</a></h3>
<p class="iv-card-sum">{esc(topics)}{'…' if len(c['sections']) > 3 else ''}</p>
<div class="iv-card-foot"><div class="iv-plan"><div class="iv-mix-bar">{segs}</div><span>{c['ntopics']}</span></div></div>
</li>"""


def topic_card(root: str, t: dict) -> str:
    samples = "".join(f"<li>{inline(q.text)}</li>" for q in t["questions"][:2])
    n_ans = sum(1 for q in t["questions"] if q.answers)
    return f"""<li class="iv-card iv-topic-card" style="--topic:{t['color']}" data-filter-item data-search="{esc(t['name'])} {esc(t['desc'])}" data-cat="topic">
<div class="iv-card-top"><span class="iv-card-count">{len(t['questions'])} 道题</span><span>{n_ans} 附答案</span></div>
<h3 class="iv-card-name"><a href="{root}topics/{t['id']}.html">{esc(t['name'])}</a></h3>
<p class="iv-card-sum">{esc(t['desc'])}</p>
<ul class="iv-samples">{samples}</ul>
</li>"""


# --------------------------------------------------------------------------- pages


def build_index():
    root = ""
    topic_cards = "".join(topic_card(root, t) for t in TOPICS)
    blocks = []
    for cat in CATEGORY_ORDER:
        comps = [c for c in COMPANIES if c["category"] == cat]
        if not comps:
            continue
        cards = "".join(company_card(root, c, "var(--blueprint)") for c in comps)
        blocks.append(f"""<section class="iv-group" data-group-block style="--group:var(--ink)">
<header class="iv-group-head"><h2>{esc(cat)}</h2><p>{esc(CATEGORY_META[cat])}</p></header>
<ul class="iv-grid">{cards}</ul></section>""")

    body = f"""<main id="main" class="iv-page" tabindex="-1">
<section class="iv-hero">
<div>
<p class="iv-kicker">AI Engineering Interviews · 中文速查</p>
<h1>AI 工程面试题库</h1>
<p class="iv-lede">41 家公司、{TOTAL_Q} 道真实出现过的 AI 工程面试题，按公司与主题双重索引。{TOTAL_ANSWERS} 道附原文答案链接，其余保留原题与出处；119 道通用题另有本站整理的中文答题要点。</p>
</div>
{stats_box()}
</section>

<div class="iv-controls">
<div class="iv-search"><label class="iv-search-label" for="filterInput">搜索公司 / 岗位 / 主题</label><input id="filterInput" type="search" placeholder="输入关键词（按 / 聚焦）" aria-label="搜索公司、岗位或主题"></div>
<div class="iv-search-row">
<fieldset class="iv-filter"><legend>筛选</legend>
<label class="iv-chip"><input type="radio" name="cat" value="all" checked><span>全部</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="topic"><span>主题</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="前沿 AI 实验室"><span>前沿实验室</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="大型科技公司的 AI 组织"><span>大厂</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="中国互联网公司"><span>中国互联网</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="AI 基础设施与平台公司"><span>基础设施</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="AI 原生应用公司"><span>AI 原生</span></label>
<label class="iv-chip"><input type="radio" name="cat" value="前向部署与企业级 AI"><span>前向部署</span></label>
</fieldset>
<span class="iv-count" id="filterCount" role="status" aria-live="polite">{len(TOPICS) + len(COMPANIES)} / {len(TOPICS) + len(COMPANIES)} 项</span>
</div>
<p id="filterEmpty" class="iv-empty" hidden>没有匹配的公司或主题，换个关键词试试。</p>
</div>

<section class="iv-group" data-group-block style="--group:var(--blueprint)">
<header class="iv-group-head"><h2>10 大主题速查</h2><p>跨公司反复出现的题目只在这里列一次，并标注会问它的公司。先把这 119 道吃透，再看目标公司。</p></header>
<ul class="iv-grid">{topic_cards}</ul>
</section>

{''.join(blocks)}

<section class="iv-group">
<header class="iv-group-head"><h2>怎么用</h2><p>把它当成地图，而不是脚本。面试流程会随团队、级别和地区变化。</p></header>
<div class="notes">
<div class="note"><h3>1 · 先过通用题</h3><p>10 大主题里的 119 道题覆盖了大多数公司的共同考点。先自己口述答案，再展开对照要点。</p></div>
<div class="note"><h3>2 · 再看目标公司</h3><p>公司页给出公开报道的岗位与流程、按主题分组的专属题，以及这家公司会问的通用题清单。</p></div>
<div class="note"><h3>3 · 用搜索补漏</h3><p>记住某个概念但想不起完整题目时，用题目与要点搜索按关键词定位，再回到主题页系统复习。</p></div>
</div></section>
</main>"""
    (OUT / "index.html").write_text(page(f"{SITE_NAME} · 41 家公司 · {TOTAL_Q} 道题", "按公司分类的 AI 工程面试题库中文版：41 家公司、782 道题、10 大主题，附原文答案链接与中文答题要点。", root, body, "home"), encoding="utf-8")


def build_companies_index():
    root = ""
    blocks = []
    for cat in CATEGORY_ORDER:
        comps = [c for c in COMPANIES if c["category"] == cat]
        if not comps:
            continue
        cards = "".join(f"""<li class="iv-card" data-filter-item data-search="{esc(c['name'])} {esc(c['roles'])}" data-cat="{esc(cat)}">
<div class="iv-card-top"><span class="iv-card-count">{c['nq']} 道题</span><span>{c['ntopics']} 主题</span></div>
<h3 class="iv-card-name"><a href="companies/{c['id']}.html">{esc(c['short'])}</a></h3>
<p class="iv-card-sum">{esc(c['category'])}</p>
</li>""" for c in comps)
        blocks.append(f"""<section class="iv-group" data-group-block style="--group:var(--ink)">
<header class="iv-group-head"><h2>{esc(cat)}</h2><p>{esc(CATEGORY_META[cat])} · {len(comps)} 家公司</p></header>
<ul class="iv-grid">{cards}</ul></section>""")
    body = f"""<main id="main" class="iv-page" tabindex="-1">
<section class="iv-hero">
<div><p class="iv-kicker">Companies</p><h1>41 家公司</h1>
<p class="iv-lede">多数公司页包含：公开报道的岗位与面试流程、按板块分组的公司专属题、以及这家公司会问到的通用题清单。</p></div>
{stats_box()}
</section>
<div class="iv-controls">
<div class="iv-search"><label class="iv-search-label" for="filterInput">搜索公司或岗位</label><input id="filterInput" type="search" placeholder="输入关键词（按 / 聚焦）" aria-label="搜索公司或岗位"></div>
<div class="iv-search-row"><span class="iv-count" id="filterCount" role="status" aria-live="polite">{len(COMPANIES)} / {len(COMPANIES)} 家</span></div>
<p id="filterEmpty" class="iv-empty" hidden>没有匹配的公司，换个关键词试试。</p>
</div>
{''.join(blocks)}
</main>"""
    (OUT / "companies.html").write_text(page("公司索引 · " + SITE_NAME, "41 家 AI 公司的面试题索引。", root, body, "companies"), encoding="utf-8")


def build_topic(t: dict):
    root = "../"
    items = []
    for i, q in enumerate(t["questions"], 1):
        tags = []
        if q.companies:
            tags.append("".join(company_link(root, c["name"]) for c in q.companies))
        if q.answers:
            tags.append(f'<span class="iv-tag">{len(q.answers)} 条原文答案</span>')
        items.append(f"""<li class="q-item" data-filter-item data-search="{esc(q.text)}" data-cat="{t['id']}">
<span class="q-num">{num(i)}</span>
<div class="q-body">
<h3><a class="q-link" href="../q/{q.id}.html">{inline(q.text)}</a></h3>
<div class="q-tags">{''.join(tags)}</div>
{answer_details(q, root)}
</div></li>""")
    body = f"""<main id="main" class="iv-page" tabindex="-1">
<article class="iv-article" style="--group:{t['color']}">
<nav class="iv-crumbs" aria-label="面包屑"><ol><li><a href="../index.html">目录</a></li><li>主题</li><li aria-current="page">{esc(t['name'])}</li></ol></nav>
<header class="iv-q-head">
<p class="iv-kicker">Topic · {t['id'].upper()}</p>
<h1>{esc(t['name'])}</h1>
<p class="iv-meta"><span class="iv-kind">{len(t['questions'])} 道题</span><span class="iv-min">{sum(1 for q in t['questions'] if q.answers)} 道附原文答案</span><span class="iv-min">{sum(1 for q in t['questions'] if q.know)} 道有本站要点</span></p>
</header>
<p class="iv-lede" style="margin-bottom:26px">{esc(t['desc'])}</p>
<div class="iv-controls iv-controls-slim">
<div class="iv-search"><label class="iv-search-label" for="filterInput">在本主题内搜索题目</label><input id="filterInput" type="search" placeholder="输入关键词" aria-label="在本主题内搜索题目"></div>
<div class="iv-toolbar">
<button class="btn" id="expandAll" type="button">全部展开</button>
<button class="btn" id="collapseAll" type="button">全部收起</button>
<span class="iv-count" id="filterCount" role="status" aria-live="polite">{len(t['questions'])} / {len(t['questions'])} 道</span>
</div>
<p id="filterEmpty" class="iv-empty" hidden>没有匹配的题目，换个关键词试试。</p>
</div>
<h2 class="iv-label">题目</h2>
<ol class="q-list">{''.join(items)}</ol>
</article>
</main>"""
    (OUT / "topics" / f"{t['id']}.html").write_text(
        page(f"{t['name']} · 面试题 · {SITE_NAME}", f"{t['name']}：{t['desc']}", root, body), encoding="utf-8")


def build_question(q: Question):
    root = "../"
    t = next(x for x in TOPICS if x["id"] == q.topic_id)
    idx = t["questions"].index(q)
    k = q.know or {}
    long = " q-long" if len(q.text) > 34 else ""

    company_chips = "".join(company_link(root, c["name"]) for c in q.companies) or '<span class="iv-tag">未标注公司</span>'
    answer_links = "".join(
        f'<li><a href="{esc(a["url"])}" target="_blank" rel="noopener">{inline(a["label"])}</a><span class="iv-src">{esc(domain_label(a["url"]))}</span></li>'
        for a in q.answers
    )
    if answer_links:
        answers_section = f"""<section class="iv-section"><h2 class="iv-label">原文答案链接</h2>
<ul class="iv-answers-list">{answer_links}</ul>
<p class="iv-try" style="border-top:0;margin-top:10px">链接指向 Outcome School 等公开来源，非本站内容。</p></section>"""
    else:
        answers_section = """<section class="iv-section"><h2 class="iv-label">原文答案链接</h2>
<p class="iv-empty">这道题在源仓库中没有附答案链接，可先用上面的要点自查，再顺着主题页补齐相关知识点。</p></section>"""

    wrong_block = ""
    if k.get("wrong"):
        items = "".join(f'<li><p class="iv-wrong-a">{inline(w)}</p></li>' for w in k["wrong"])
        wrong_block = f"""<section class="iv-section"><h2 class="iv-label">常见错误说法</h2>
<div class="iv-answer" style="background:var(--bg)"><div class="iv-answer-body"><ul class="iv-wrong">{items}</ul></div></div></section>"""

    points_html = "".join(f"<li>{inline(p)}</li>" for p in k.get("points", []))
    formula_html = f"<pre><code>{esc(k['formula'])}</code></pre>" if k.get("formula") else ""
    short_html = inline(k["short"]) if k.get("short") else "（暂无）"

    related = "".join(
        f'<li><a href="{root}q/{r.id}.html">{inline(clip(r.text, 34))}</a></li>'
        for r in t["questions"][max(0, idx - 3): idx] + t["questions"][idx + 1: idx + 4]
    )
    prev_q = t["questions"][idx - 1] if idx > 0 else None
    next_q = t["questions"][idx + 1] if idx + 1 < len(t["questions"]) else None
    prev_html = (
        f'<a href="{root}q/{prev_q.id}.html" rel="prev"><span>上一题</span>{inline(clip(prev_q.text, 34))}</a>'
        if prev_q else '<span class="iv-pager-empty" aria-hidden="true"></span>'
    )
    next_html = (
        f'<a href="{root}q/{next_q.id}.html" rel="next"><span>下一题</span>{inline(clip(next_q.text, 34))}</a>'
        if next_q else '<span class="iv-pager-empty" aria-hidden="true"></span>'
    )
    pager = f"""<nav class="iv-pager" aria-label="同主题翻页">
{prev_html}
<a class="iv-pager-up" href="{root}topics/{t['id']}.html"><span>主题</span>{esc(t['name'])}</a>
{next_html}
</nav>"""

    body = f"""<main id="main" class="iv-page" tabindex="-1">
<article class="iv-article iv-question" style="--group:{t['color']}">
<nav class="iv-crumbs" aria-label="面包屑"><ol>
<li><a href="{root}index.html">目录</a></li>
<li><a href="{root}topics/{t['id']}.html">{esc(t['name'])}</a></li>
<li aria-current="page">第 {idx + 1} 题</li></ol></nav>
<header class="iv-q-head">
<p class="iv-kicker">{esc(t['name'])} · Question {num(idx + 1)}</p>
<h1 class="q-title{long}">{inline(q.text)}</h1>
<p class="iv-meta">
<span class="iv-kind">{'有答题要点' if q.know else '仅有原文链接'}</span>
<span class="iv-min">{len(q.companies)} 家公司出现</span>
<span class="iv-min">{len(q.answers)} 条原文答案</span>
</p>
<p class="iv-meta" style="margin-top:10px"><a class="iv-tag" href="{root}topics/{t['id']}.html">{esc(t['name'])}</a></p>
</header>

<section class="iv-section" aria-labelledby="spec">
<h2 id="spec" class="iv-label">本题信息</h2>
<dl class="iv-spec">
<div><dt>主题</dt><dd><a href="{root}topics/{t['id']}.html">{esc(t['name'])}</a></dd></div>
<div><dt>出现于</dt><dd>{len(q.companies)} 家公司</dd></div>
<div><dt>原文答案</dt><dd>{len(q.answers)} 条链接</dd></div>
</dl>
<p class="iv-try">先自己口述一遍答案，再展开对照。面试里能讲清取舍，比背结论重要。</p>
</section>

<section class="iv-answers" aria-labelledby="answer">
<h2 id="answer" class="iv-label">答案</h2>
<details class="iv-answer"><summary>展开简短答案</summary><div class="iv-answer-body"><p>{short_html}</p></div></details>
<details class="iv-answer"><summary>展开完整答案（要点{ ' + 公式' if k.get('formula') else '' }）</summary>
<div class="iv-answer-body iv-prose"><ul>{points_html}</ul>{formula_html}</div></details>
</section>

{wrong_block}

<section class="iv-section"><h2 class="iv-label">出现于</h2><p class="iv-meta">{company_chips}</p>
<p class="iv-try" style="border-top:0;margin-top:10px">{'公司页里有这家公司的岗位、流程与专属题。' if q.companies else '源仓库没有标注具体公司，可按主题浏览相近的题。'}</p></section>

{answers_section}

{lab_chips(root, q.id)}
<section class="iv-related"><h2>同主题的其他题</h2><ul>{related}</ul></section>

<button class="btn" id="copyLink" type="button">复制本页链接</button>
</article>
{pager}
</main>"""
    ld = {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": zh(q.text)[:120],
        "inLanguage": "zh-CN",
        "educationalLevel": "working",
        "learningResourceType": "Interview question",
        "about": t["name"],
        "isAccessibleForFree": True,
        "isPartOf": {"@type": "Course", "name": SITE_NAME, "url": REPO},
        "hasPart": [{
            "@type": "Question",
            "name": zh(q.text),
            "acceptedAnswer": {"@type": "Answer", "text": k.get("short", "")},
        }],
    }
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("<", "\\u003c") + "</script>"
    short_title = clip(zh(q.text), 30)
    desc = clip(zh(q.text), 120)
    (OUT / "q" / f"{q.id}.html").write_text(
        page(f"{short_title} · {t['name']} · {SITE_NAME}", desc, root, body, extra_head=extra), encoding="utf-8")


def build_company(c: dict):
    root = "../"
    sections = []
    n = 0
    for s in c["sections"]:
        items = []
        for q in s["questions"]:
            n += 1
            links = "".join(
                f'<li><a href="{esc(a["url"])}" target="_blank" rel="noopener">{inline(a["label"])}</a><span class="iv-src">{esc(domain_label(a["url"]))}</span></li>'
                for a in q["answers"]
            )
            detail = (f'<details class="q-answer"><summary>{len(q["answers"])} 条原文答案</summary><div class="q-answer-body"><ul class="iv-answers-list">{links}</ul></div></details>'
                      if links else '<p class="q-tags" style="margin-top:4px">源仓库未附答案链接</p>')
            items.append(f"""<li class="q-item" id="q{n}"><span class="q-num">{num(n)}</span>
<div class="q-body"><h3>{inline(q['text'])}</h3><div class="q-tags"><span class="iv-tag">{esc(s['name'])}</span></div>{detail}</div></li>""")
        sections.append(f"""<section class="iv-group" style="--group:var(--ink)">
<header class="iv-group-head" style="grid-template-columns:minmax(0,1fr)"><h2 style="font-size:1.5rem">{esc(s['name'])}</h2><p>{len(s['questions'])} 道题</p></header>
<ol class="q-list">{''.join(items)}</ol></section>""")

    cross = CROSS_FOR_COMPANY[c["id"]]
    cross_html = ""
    if cross:
        chips = "".join(f'<li><a href="{root}q/{q.id}.html">{inline(clip(q.text, 44))}</a></li>' for q in cross)
        cross_html = f"""<section class="iv-section"><h2 class="iv-label">这家公司会问的通用题（{len(cross)}）</h2>
<div class="iv-related"><ul>{chips}</ul></div></section>"""

    notes = f"""<div class="notes">
<div class="note"><h2>覆盖岗位</h2><p>{inline(c['roles']) or '源仓库未列出'}</p></div>
<div class="note"><h2>公开报道的面试流程</h2><p>{inline(c['process']) or '源仓库未列出'}</p></div>
{'<div class="note"><h2>另外还要准备</h2><p>' + inline_with_links(c['prepare'], root) + '</p></div>' if c['prepare'] else ''}
</div>"""

    body = f"""<main id="main" class="iv-page" tabindex="-1">
<article class="iv-article" style="--group:var(--ink)">
<nav class="iv-crumbs" aria-label="面包屑"><ol><li><a href="{root}index.html">目录</a></li><li><a href="{root}companies.html">公司</a></li><li aria-current="page">{esc(c['short'])}</li></ol></nav>
<header class="iv-q-head">
<p class="iv-kicker">{esc(c['category'])}</p>
<h1{' class="q-long"' if len(c['name']) > 18 else ''}>{esc(c['name'])}</h1>
<p class="iv-meta"><span class="iv-kind">{c['nq']} 道专属题</span><span class="iv-min">{c['ntopics']} 个板块</span><span class="iv-min">{len(cross)} 道通用题</span></p>
</header>
{notes}
{cross_html}
<section class="iv-section" style="margin-top:30px"><h2 class="iv-label">公司专属题</h2>
<p class="iv-try" style="border-top:0">按主题分组。没有答案链接的题目，可以先到「10 大主题」里找对应的通用解法。</p></section>
{''.join(sections)}
</article>
<nav class="iv-pager" aria-label="公司翻页"><a href="{root}companies.html"><span>全部</span>公司索引</a><span></span><span></span></nav>
</main>"""
    (OUT / "companies" / f"{c['id']}.html").write_text(
        page(f"{c['short']} 面试题 · {SITE_NAME}", f"{c['short']} 的 AI 工程面试题：{c['nq']} 道，覆盖 {c['ntopics']} 个板块。", root, body), encoding="utf-8")


LABS = (
    ("kv", "KV 缓存计算器", "拖动层数、KV 头数、上下文与并发，看 KV 缓存怎么把显存吃满。"),
    ("finetune", "微调显存预算", "全量 / LoRA / QLoRA 三种方案，逐项拆开权重、梯度、优化器与激活。"),
    ("sampling", "采样实验室", "温度、top-k、top-p 同时作用在 12 个候选上，实时看概率如何被截断。"),
    ("roofline", "吞吐 roofline", "给定模型与带宽，算 batch 多大时从带宽受限转为算力受限。"),
    ("attention", "注意力热力图", "9 个 token 的 Q/K，拖动 d、温度与掩码，看每行如何分配注意力。"),
)

LAB_LINKS = {
    "t0q1": ["kv"], "t1q1": ["kv"], "t1q7": ["kv"], "t0q2": ["kv"],
    "t4q3": ["finetune"], "t4q4": ["finetune"], "t4q8": ["finetune"],
    "t0q11": ["sampling"], "t9q4": ["sampling"],
    "t1q9": ["roofline"], "t1q0": ["roofline"],
    "t0q0": ["attention"], "t0q15": ["attention"], "t9q0": ["attention"], "t0q13": ["attention"],
}


def build_labs():
    tpl = ROOT / "scripts" / "labs_templates"
    cards = "".join(
        f'<li class="iv-card" style="--group:var(--lab-{["blue","brown-1","brown-2","brown-3"][i % 4]})"><div class="iv-card-top">'
        f'<span class="iv-card-count">Lab {i + 1:02d}</span><span>交互</span></div>'
        f'<h3 class="iv-card-name"><a href="labs/{lid}.html">{esc(title)}</a></h3>'
        f'<p class="iv-card-sum">{esc(desc)}</p></li>'
        for i, (lid, title, desc) in enumerate(LABS)
    )
    body = (tpl / "index.html").read_text(encoding="utf-8").replace("{cards}", cards)
    (OUT / "labs.html").write_text(
        page("可视化实验室 · " + SITE_NAME, "四个交互实验：KV 缓存、微调显存、采样分布、吞吐 roofline。", "", body, "labs"),
        encoding="utf-8")
    (OUT / "labs").mkdir(exist_ok=True)
    for lid, title, desc in LABS:
        body = (tpl / f"{lid}.html").read_text(encoding="utf-8")
        (OUT / "labs" / f"{lid}.html").write_text(
            page(f"{title} · 可视化 · {SITE_NAME}", desc, "../", body, "labs"), encoding="utf-8")


def lab_chips(root: str, qid: str) -> str:
    ids = LAB_LINKS.get(qid, [])
    if not ids:
        return ""
    items = "".join(
        f'<li><a href="{root}labs/{lid}.html">{esc(title)}</a></li>'
        for lid, title, _ in LABS if lid in ids
    )
    return f'<section class="iv-related"><h2>相关可视化</h2><ul>{items}</ul></section>'


def build_search():
    root = ""
    body = f"""<main id="main" class="iv-page" tabindex="-1">
<section class="iv-hero">
<div><p class="iv-kicker">Search</p><h1>题目与要点搜索</h1>
<p class="iv-lede">在 {TOTAL_Q} 道题里按关键词定位：模型名、技术名词、公司名都可以。数据在浏览器本地过滤，不会上传。</p></div>
{stats_box()}
</section>
<div class="iv-controls">
<div class="iv-search"><label class="iv-search-label" for="searchInput">搜索 {TOTAL_Q} 道题</label><input id="searchInput" type="search" placeholder="例如：KV 缓存、DPO、提示注入、字节跳动" aria-label="搜索题目"></div>
<div class="iv-search-row"><span class="iv-count" id="searchCount" role="status" aria-live="polite">输入关键词开始</span></div>
</div>
<h2 class="iv-label">结果</h2>
<ol class="q-list" id="results"><li class="iv-empty">开始输入以搜索。</li></ol>
</main>
<script src="assets/search.js" defer></script>"""
    (OUT / "search.html").write_text(page("搜索 · " + SITE_NAME, "题目与要点搜索 782 道 AI 工程面试题。", root, body, "search"), encoding="utf-8")

    data = []
    for t in TOPICS:
        for q in t["questions"]:
            data.append({"i": q.id, "q": zh(q.text), "t": t["name"], "c": [fix_terms(SHORT_NAME.get(x["name"], x["name"])) for x in q.companies], "a": len(q.answers), "s": zh((q.know or {}).get("short", ""))[:140]})
    for c in COMPANIES:
        n = 0
        for sec in c["sections"]:
            for q in sec["questions"]:
                n += 1
                data.append({"i": None, "q": zh(q["text"]), "t": sec["name"], "c": [c["short"]],
                             "a": len(q["answers"]), "u": f"companies/{c['id']}.html#q{n}"})
    (OUT / "assets" / "data").mkdir(exist_ok=True)
    (OUT / "assets" / "data" / "questions.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def build_about():
    root = ""
    body = f"""<main id="main" class="iv-page" tabindex="-1">
<article class="iv-article">
<nav class="iv-crumbs" aria-label="面包屑"><ol><li><a href="index.html">目录</a></li><li aria-current="page">关于</li></ol></nav>
<header class="iv-q-head"><p class="iv-kicker">About</p><h1>关于这个站点</h1>
<p class="iv-lede">把一份 41 家公司、{TOTAL_Q} 道题的中文面经清单，做成可以按主题和公司两边翻的速查手册。</p></header>

<section class="iv-section"><h2 class="iv-label">内容从哪来</h2>
<p>题目与公司信息来自 <a href="{REPO}" target="_blank" rel="noopener">ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn</a>（Apache-2.0），它是 <a href="{UPSTREAM}" target="_blank" rel="noopener">pallavi-shekhar/ai-engineering-interview-questions-company-wise</a> 的中文版。题目本身整理自公开报道的面试经历，不包含机密内容。</p>
<p>原文答案链接指向 <a href="{SCHOOL}" target="_blank" rel="noopener">Outcome School</a> 的博客、视频或 LinkedIn 帖，版权归原作者所有，本站只做索引。</p>
</section>

<section class="iv-section"><h2 class="iv-label">答题要点是什么</h2>
<p>10 大主题下的 119 道通用题，每题有一份本站整理的「简短答案 + 完整要点」，其中 4 道另附「常见错误说法」。它是学习用的自查材料，<strong>不是官方标准答案</strong>，也不代表任何公司的评分标准。面试里请按自己的理解组织语言，并优先核对原始资料。</p>
<p>公司专属题只保留题目与原文答案链接，不代写答案——那些题往往绑定具体团队与业务背景，泛化的答案反而有害。</p>
</section>

<section class="iv-section"><h2 class="iv-label">适合的岗位</h2>
<p>AI 工程师、生成式 AI 工程师、LLM 工程师、Agentic AI / AI Agent 工程师、机器学习工程师、研究工程师、应用科学家、前向部署工程师、AI 解决方案架构师、AI 平台工程师、应用 AI 工程师、LLM 推理与性能工程师、MLOps / LLMOps 工程师。</p>
</section>

<section class="iv-section"><h2 class="iv-label">怎么读</h2>
<ol>
<li><strong>先通用题</strong>：10 大主题覆盖大多数公司的共同考点，每题先口述再展开。</li>
<li><strong>再公司页</strong>：看岗位、流程、专属题，以及这家公司会问的通用题清单。</li>
<li><strong>最后搜索</strong>：用关键词把散落的知识点串起来，回到主题页系统复习。</li>
</ol>
</section>

<section class="iv-section"><h2 class="iv-label">站点怎么做的</h2>
<dl class="note" style="border:1px solid var(--rule-soft);background:var(--bg-surface);padding:14px 16px">
<dt>生成方式</dt><dd>Python 静态生成，Markdown → JSON → HTML，无前端框架、无追踪脚本。</dd>
<dt>版式</dt><dd>参照 aiengineeringfromscratch.com/interviews 的蓝图风格：纸面点阵、硬阴影、像素显示字体、等宽元信息。</dd>
<dt>字体</dt><dd>Fusion Pixel（中文像素）、VT323、Source Serif 4、JetBrains Mono，均本地托管。</dd>
<dt>构建日期</dt><dd>{BUILD_DATE}</dd>
</dl>
</section>

<section class="iv-section"><h2 class="iv-label">由 Outcome School 整理与维护</h2>
<p>英文原版与答案内容由 Outcome School 维护：<a href="https://outcomeschool.com/program/ai-and-machine-learning" target="_blank" rel="noopener">AI and Machine Learning Program</a> ·
<a href="https://youtube.com/@OutcomeSchool" target="_blank" rel="noopener">YouTube</a> ·
<a href="https://x.com/outcome_school" target="_blank" rel="noopener">X / Twitter</a> ·
<a href="https://www.linkedin.com/company/outcomeschool" target="_blank" rel="noopener">LinkedIn</a> ·
<a href="https://github.com/OutcomeSchool" target="_blank" rel="noopener">GitHub</a></p>
<p>按主题组织的题库另见 <a href="https://github.com/amitshekhariitbhu/ai-engineering-interview-questions" target="_blank" rel="noopener">AI Engineering Interview Questions and Answers</a>。</p>
</section>

<section class="iv-section"><h2 class="iv-label">免责声明</h2>
<p>面试流程会随团队、级别、地区和时间变化，请把每个公司页当作「这家公司关心什么」的地图，而不是「你一定会被问到什么」的脚本。发现翻译或事实错误，欢迎到源仓库提 Issue。</p>
</section>
</article>
</main>"""
    (OUT / "about.html").write_text(page("关于 · " + SITE_NAME, "站点说明、内容来源与免责声明。", root, body, "about"), encoding="utf-8")


def build_assets():
    import shutil
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for name in ("site.css", "site.js", "search.js", "lab-kv.js", "lab-finetune.js", "lab-sampling.js", "lab-roofline.js", "lab-attention.js"):
        shutil.copyfile(ROOT / "assets" / name, OUT / "assets" / name)
    shutil.copyfile(ROOT / "assets" / "fonts" / "fonts.css", OUT / "assets" / "fonts" / "fonts.css")
    for f in (ROOT / "assets" / "fonts").glob("*.woff2"):
        shutil.copyfile(f, OUT / "assets" / "fonts" / f.name)
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" fill="#fafaf5"/>
<rect x="4" y="4" width="10" height="10" fill="#3553ff"/>
<rect x="18" y="4" width="10" height="10" fill="#1a1a1a"/>
<rect x="4" y="18" width="10" height="10" fill="#1a1a1a"/>
<rect x="18" y="18" width="10" height="10" fill="#3553ff"/>
</svg>"""
    (OUT / "favicon.svg").write_text(favicon, encoding="utf-8")


def subset_font():
    """把中文字体裁到页面实际用到的字符，43KB 左右而不是 685KB。"""
    from fontTools import subset as ftsubset
    chars = set()
    for f in OUT.rglob("*.html"):
        chars |= set(f.read_text(encoding="utf-8"))
    chars |= set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz，。、；：？！“”‘’（）《》—…·／")
    text = "".join(sorted(c for c in chars if c.isprintable() or c in "\n\t"))
    tmp = OUT / "assets" / "fonts" / "_chars.txt"
    tmp.write_text(text, encoding="utf-8")
    args = [
        str(ROOT / "assets" / "fonts" / "source" / "fusion-pixel-zh_hans.woff2"),
        f"--text-file={tmp}",
        "--flavor=woff2",
        "--layout-features=*",
        f"--output-file={OUT / 'assets' / 'fonts' / 'fusion-pixel-zh.woff2'}",
    ]
    ftsubset.main(args)
    tmp.unlink()
    size = (OUT / "assets" / "fonts" / "fusion-pixel-zh.woff2").stat().st_size
    print(f"font subset: {len(text)} chars, {size // 1024} KB")


def main():
    for d in ("q", "topics", "companies"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    build_assets()
    build_index()
    build_companies_index()
    for t in TOPICS:
        build_topic(t)
    for q in Q_BY_ID.values():
        build_question(q)
    for c in COMPANIES:
        build_company(c)
    build_search()
    build_labs()
    build_about()
    subset_font()
    meta = {
        "companies": len(COMPANIES),
        "questions_total": TOTAL_Q,
        "cross_questions": sum(len(t["questions"]) for t in TOPICS),
        "company_questions": sum(c["nq"] for c in COMPANIES),
        "answers": TOTAL_ANSWERS,
        "question_pages": len(Q_BY_ID),
        "knowledge": len(KNOWLEDGE),
    }
    (OUT / "build-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
