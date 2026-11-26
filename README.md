# AI 工程面试题库 · 中文版（静态站点）

把 [ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn](https://github.com/ninetyhe-90/ai-engineering-interview-questions-company-wise-zh-cn)
（Apache-2.0）的 41 家公司、782 道题，做成可按主题与公司双向浏览的静态站点；版式参照
[aiengineeringfromscratch.com/interviews](https://aiengineeringfromscratch.com/interviews/post-training/qlora-on-one-gpu)
的蓝图风格（纸面点阵、硬阴影、像素显示字体、等宽元信息、可折叠答案）。

## 结构

```
src/README.zh.md      源仓库中文 README（数据源，勿改）
src/corpus.json       解析后的结构化题库（脚本生成）
knowledge/*.json      119 道通用题的中文答题要点（手写）
scripts/parse.py      Markdown → corpus.json
scripts/build.py      corpus + knowledge → site/（静态 HTML）
assets/site.css       设计系统（源文件，构建时复制到 site/assets）
assets/site.js        交互：主题、筛选、展开
assets/search.js      全文搜索（读取 assets/data/questions.json）
assets/fonts/         拉丁字体 + 中文像素字体源文件（source/）
site/                 构建产物（可直接托管）
```

产物共 180 个页面：首页、公司索引、题目搜索、可视化实验室（5 个交互实验：KV 缓存、微调显存、采样、roofline、注意力热力图）、关于、10 个主题页、41 个公司页、119 个题目页。

## 构建

```bash
python3 scripts/parse.py     # src/README.zh.md → src/corpus.json
python3 scripts/build.py     # → site/
```

`build.py` 最后会把中文字体裁到页面实际用到的字符（685 KB → 约 42 KB），
所以每次改动文案后都要重新构建。

本地预览：

```bash
cd site && python3 -m http.server 8787
# http://127.0.0.1:8787/
```

搜索页通过 `fetch` 读取 JSON，必须走 HTTP，直接双击 HTML 会退化为提示信息。

## 内容约定

- 题目、公司、岗位、流程均来自源仓库，逐条保留；只做中文标点归一（半角 → 全角）。
- 原文答案链接保留并标注来源域名，指向 Outcome School 等原作者内容。
- 10 大主题下的 119 道通用题有本站整理的「简短答案 / 完整要点 / 常见错误」，
  属学习材料，**不是官方标准答案**；公司专属题不代写答案。
- 无追踪脚本、无外部请求；字体全部本地托管。

## 许可

题目与公司信息：Apache-2.0，来自上述源仓库；答案链接版权归原作者。
本站新增的答题要点与页面代码可自由用于学习，转载请注明来源。
