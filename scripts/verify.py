#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立验收：直接读源 README，与生成的站点对比，不依赖 parse.py 的中间产物。"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "src" / "README.zh.md").read_text(encoding="utf-8")
SITE = ROOT / "site"


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[\s\u00a0]+", "", s)
    s = s.replace(",", "，").replace("?", "？").replace(":", "：").replace(";", "；")
    return s


def main():
    # --- source side: every top-level bullet inside the question sections
    src_q = []
    h2 = h3 = h4 = None
    for line in SRC.split("\n"):
        m = re.match(r"^(#{2,4}) (.*)$", line)
        if m:
            lvl, title = len(m.group(1)), m.group(2)
            if lvl == 2:
                h2, h3, h4 = title, None, None
            elif lvl == 3:
                h3, h4 = title, None
            else:
                h4 = title
            continue
        if line.startswith("- ") and h2 in (
            "跨公司通用面试题", "前沿 AI 实验室", "大型科技公司的 AI 组织",
            "中国互联网公司", "AI 基础设施与平台公司", "AI 原生应用公司", "前向部署与企业级 AI",
        ):
            src_q.append((h2, h3, h4, line[2:].strip()))

    # --- site side
    corpus = json.loads((ROOT / "src" / "corpus.json").read_text(encoding="utf-8"))
    site_q = []
    for t in corpus["cross_topics"]:
        for q in t["questions"]:
            site_q.append(("cross", t["name"], q["text"]))
    for c in corpus["companies"]:
        for s in c["sections"]:
            for q in s["questions"]:
                site_q.append(("company", c["name"], q["text"]))

    print(f"source bullets: {len(src_q)}   parsed questions: {len(site_q)}")
    src_norm = {norm(q[3]) for q in src_q}
    site_norm = {norm(q[2]) for q in site_q}
    missing = [q for q in src_q if norm(q[3]) not in site_norm]
    print(f"missing from site: {len(missing)}")
    for m in missing[:10]:
        print("  -", m[1], "|", m[3][:80])

    # --- answer urls preserved
    src_urls = set(re.findall(r"\((https?://[^)]+)\)", SRC))
    site_urls = set()
    for f in SITE.rglob("*.html"):
        site_urls |= set(html.unescape(u) for u in re.findall(r'href="(https?://[^"]+)"', f.read_text(encoding="utf-8")))
    print(f"answer urls in source: {len(src_urls)}   on site: {len(src_urls & site_urls)}   missing: {len(src_urls - site_urls)}")
    for u in list(src_urls - site_urls)[:10]:
        print("  -", u)

    # --- company pages exist and counts match
    problems = []
    slug = {}
    import re as _re
    src_build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
    block = _re.search(r"COMPANY_IDS = \{(.*?)\n\}", src_build, _re.S).group(1)
    slug = dict(_re.findall(r'"([^"]+)": "([^"]+)"', block))
    for c in corpus["companies"]:
        n = sum(len(s["questions"]) for s in c["sections"])
        path = SITE / "companies" / f"{slug.get(c['name'], '')}.html"
        if not path.exists() or f"{n} 道专属题" not in path.read_text(encoding="utf-8"):
            problems.append((c["name"], n))
    print(f"company pages with matching counts: {len(corpus['companies']) - len(problems)}/{len(corpus['companies'])}")

    # --- question pages
    qpages = list((SITE / "q").glob("*.html"))
    print(f"question pages: {len(qpages)} (expected {len(corpus['cross_topics']) and sum(len(t['questions']) for t in corpus['cross_topics'])})")

    # --- internal links
    bad = []
    for f in SITE.rglob("*.html"):
        for href in re.findall(r'href="([^"]+)"', f.read_text(encoding="utf-8")):
            if href.startswith(("http", "mailto:", "#", "data:")):
                continue
            target = (f.parent / href.split("#")[0]).resolve()
            if href.split("#")[0] and not target.exists():
                bad.append((f.relative_to(SITE), href))
    print(f"broken internal links: {len(bad)}")
    for b in bad[:5]:
        print("  -", b)

    # --- html basics
    no_h1 = [f.name for f in SITE.rglob("*.html") if f.read_text(encoding="utf-8").count("<h1") != 1]
    print(f"pages without exactly one h1: {len(no_h1)}")
    print(f"total pages: {len(list(SITE.rglob('*.html')))}")
    print("OK" if not (missing or bad or no_h1 or problems) else "CHECK ABOVE")


if __name__ == "__main__":
    main()
