# Attribution

The question corpus in `src/` is derived from
[ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn](https://github.com/ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn),
licensed **Apache-2.0**. That repository aggregates 41 companies / 782 interview questions.

Design blueprint credit: layout inspiration from
[aiengineeringfromscratch.com/interviews](https://aiengineeringfromscratch.com/interviews/post-training/qlora-on-one-gpu).

## What is original here

- `scripts/parse.py`, `scripts/build.py` — the Markdown → `corpus.json` → static HTML pipeline.
- `knowledge/*.json` — Chinese answer outlines for 119 general questions, written for this site.
- `site/` — the generated static site (HTML/CSS/JS).

## Apache-2.0 obligations

- The upstream licence text is retained in `LICENSE-APACHE-2.0.txt`.
- Upstream notices are reproduced above and in the site's About page.
- Any redistribution of the derived corpus must keep this file and the licence.

## Not affiliated

This is an independent study aid. It is not endorsed by, or affiliated with, the upstream
repository's maintainers or any company named in the corpus.
