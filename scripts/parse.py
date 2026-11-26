#!/usr/bin/env python3
"""Parse the Chinese README of ai-engineering-interview-questions-company-wise-zh-cn
into a structured JSON corpus used by the static site generator."""
import json
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "README.zh.md"
OUT = Path(__file__).resolve().parent.parent / "src" / "corpus.json"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline_links(text):
    return [{"label": m.group(1), "url": m.group(2)} for m in LINK_RE.finditer(text)]


def strip_links(text):
    return LINK_RE.sub(lambda m: m.group(1), text).strip()


def slugify(name, seen=None):
    base = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", name.lower()).strip("-")
    return base or "x"


def main():
    lines = SRC.read_text(encoding="utf-8").split("\n")
    h2 = None
    h3 = None
    h4 = None
    doc = {"categories": [], "cross_topics": [], "companies": []}
    cat = None
    company = None
    cross_topic = None
    section = None
    pending_block = []  # blockquote lines for company / topic
    in_quote = False
    cur_q = None

    def flush_quote():
        nonlocal pending_block
        if pending_block:
            text = "\n".join(pending_block)
            if company is not None and section is None:
                company["notes_raw"] = company.get("notes_raw", "") + text + "\n"
            elif company is None and cross_topic is not None:
                cross_topic["note_raw"] = cross_topic.get("note_raw", "") + text + "\n"
            pending_block = []

    def close_question():
        nonlocal cur_q
        if cur_q is not None and section is not None:
            section["questions"].append(cur_q)
        cur_q = None

    i = 0
    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()
        stripped = raw.strip()

        m = re.match(r"^(#{1,4}) (.*)$", stripped)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            flush_quote()
            close_question()
            in_quote = False
            if level == 2:
                h2, h3, h4, section, company, cross_topic = title, None, None, None, None, None
                if title in ("跨公司通用面试题",):
                    cat = {"name": title, "kind": "cross"}
                    doc["categories"].append(cat)
                elif title in ("前沿 AI 实验室", "大型科技公司的 AI 组织", "中国互联网公司",
                               "AI 基础设施与平台公司", "AI 原生应用公司", "前向部署与企业级 AI"):
                    cat = {"name": title, "kind": "companies"}
                    doc["categories"].append(cat)
                else:
                    cat = None
            elif level == 3:
                h3, h4, section = title, None, None
                if cat and cat["kind"] == "cross":
                    cross_topic = {"name": title, "category": cat["name"], "questions": [],
                                   "note_raw": "", "id": slugify(title) + "-" + str(len(doc["cross_topics"]))}
                    doc["cross_topics"].append(cross_topic)
                    section = cross_topic
                elif cat and cat["kind"] == "companies":
                    company = {"name": title, "category": cat["name"], "notes_raw": "",
                               "sections": [], "id": slugify(title)}
                    doc["companies"].append(company)
            elif level == 4:
                h4 = title
                if company is not None:
                    section = {"name": title, "questions": []}
                    company["sections"].append(section)
                elif cross_topic is not None:
                    section = cross_topic
            i += 1
            continue

        if stripped.startswith("> "):
            if not in_quote:
                in_quote = True
            pending_block.append(stripped.lstrip("> ").strip())
            i += 1
            continue
        elif in_quote and stripped == "":
            pending_block.append("")
            i += 1
            continue
        else:
            if stripped:
                flush_quote()
            in_quote = False

        # Question bullet: top-level "- " (no leading spaces)
        if re.match(r"^- ", raw) and section is not None:
            close_question()
            body = raw[2:].strip()
            cur_q = {
                "text": strip_links(body),
                "raw": body,
                "links": inline_links(body),
                "companies": [],
                "answers": [],
            }
            i += 1
            continue

        # Nested metadata bullets: "  - 出现于：..." / "  - 答案：..."
        if cur_q is not None and re.match(r"^\s{2,}- ", raw):
            body = re.sub(r"^\s{2,}- ", "", raw).strip()
            if body.startswith("出现于"):
                cur_q["companies"] = [{"name": l["label"], "anchor": l["url"].lstrip("#")}
                                      for l in inline_links(body)]
            elif body.startswith("答案"):
                cur_q["answers"] = inline_links(body)
            elif core := body.strip():
                # continuation line of the question
                cur_q["text"] += " " + strip_links(core)
            i += 1
            continue

        # Continuation of a question (plain indented line)
        if cur_q is not None and raw.startswith("  ") and stripped:
            cur_q["text"] += " " + strip_links(stripped)
            i += 1
            continue

        i += 1

    close_question()
    flush_quote()

    # ---- post-process ----
    # Split company notes_raw into roles / process / prepare
    for c in doc["companies"]:
        notes = c.pop("notes_raw", "")
        roles = process = prepare = ""
        for chunk in notes.split("\n"):
            s = chunk.strip()
            if not s:
                continue
            m = re.match(r"^\*\*([^*]+?)\s*[:：]\s*\*\*\s*(.*)$", s)
            if m:
                label, rest = m.group(1), m.group(2).strip()
                if "岗位" in label:
                    roles = rest
                elif "流程" in label:
                    process = rest
                else:
                    prepare = rest
            elif s.startswith("**") and s.endswith("**"):
                continue
            elif roles and not process:
                roles += " " + s
            elif process and not prepare:
                process += " " + s
            else:
                prepare += " " + s
        c["roles"] = roles
        c["process"] = process
        c["prepare"] = prepare

    doc["stats"] = {
        "companies": len(doc["companies"]),
        "cross_questions": sum(len(t["questions"]) for t in doc["cross_topics"]),
        "company_questions": sum(len(s["questions"]) for c in doc["companies"] for s in c["sections"]),
        "topics": sum(len(c["sections"]) for c in doc["companies"]),
        "cross_topics": len(doc["cross_topics"]),
        "with_answers": sum(1 for t in doc["cross_topics"] for q in t["questions"] if q["answers"])
        + sum(1 for c in doc["companies"] for s in c["sections"] for q in s["questions"] if q["answers"]),
    }

    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(doc["stats"], ensure_ascii=False, indent=2))
    print("companies:", [c["name"] for c in doc["companies"]])
    for c in doc["companies"][:3]:
        print("---", c["name"], "roles:", c["roles"][:80], "| process:", c["process"][:80])


if __name__ == "__main__":
    main()
