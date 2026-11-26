/* 全文搜索：加载 questions.json，本地过滤与排序 */
(function () {
  "use strict";
  var input = document.getElementById("searchInput");
  var countEl = document.getElementById("searchCount");
  var list = document.getElementById("results");
  if (!input || !list) return;

  var DATA = null;
  var failed = false;

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function render(items, q) {
    if (!q) {
      list.innerHTML = '<li class="iv-empty">开始输入以搜索。</li>';
      countEl.textContent = "输入关键词开始";
      return;
    }
    if (!items.length) {
      list.innerHTML = '<li class="iv-empty">没有匹配的题目。试试更短的关键词，或换一个技术名词。</li>';
      countEl.textContent = "0 条结果";
      return;
    }
    var html = items.slice(0, 60).map(function (it, i) {
      var href = it.i ? "q/" + it.i + ".html" : it.u;
      var tags = (it.c || []).map(function (c) { return '<span class="iv-tag">' + esc(c) + "</span>"; }).join("");
      var atag = it.a ? '<span class="iv-tag">' + it.a + " 条原文答案</span>" : "";
      return '<li class="q-item"><span class="q-num">' + String(i + 1).padStart(2, "0") + "</span>" +
        '<div class="q-body"><h3><a class="q-link" href="' + href + '">' + esc(it.q) + "</a></h3>" +
        '<div class="q-tags"><span class="iv-tag">' + esc(it.t) + "</span>" + tags + atag + "</div></div></li>";
    }).join("");
    list.innerHTML = html;
    countEl.textContent = items.length + " 条结果" + (items.length > 60 ? "（显示前 60 条）" : "");
  }

  function score(it, terms) {
    var hay = (it.q + " " + it.t + " " + (it.c || []).join(" ") + " " + (it.s || "")).toLowerCase();
    var s = 0;
    for (var i = 0; i < terms.length; i++) {
      var idx = hay.indexOf(terms[i]);
      if (idx === -1) return -1;
      s += 1;
      if (it.q.toLowerCase().indexOf(terms[i]) !== -1) s += 2;
    }
    return s;
  }

  function run() {
    if (!DATA) return;
    var q = input.value.trim().toLowerCase();
    if (!q) return render([], "");
    var terms = q.split(/\s+/).filter(Boolean);
    var hits = [];
    for (var i = 0; i < DATA.length; i++) {
      var s = score(DATA[i], terms);
      if (s >= 0) hits.push([s, DATA[i]]);
    }
    hits.sort(function (a, b) { return b[0] - a[0]; });
    render(hits.map(function (h) { return h[1]; }), q);
  }

  var loading = false;
  function ensureData() {
    if (DATA || loading) return;
    loading = true;
    if (countEl) countEl.textContent = "正在加载索引…";
    fetch("assets/data/questions.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        DATA = data;
        loading = false;
        if (countEl) countEl.textContent = DATA.length + " 道题已索引";
        run();
      })
      .catch(function () {
        loading = false;
        list.innerHTML = '<li class="iv-empty">搜索索引加载失败。请通过本地服务器打开（例如 <code>python3 -m http.server</code>），而不是直接双击 HTML 文件。</li>';
        countEl.textContent = "索引未加载";
      });
  }

  input.onfocus = ensureData;
  input.oninput = function () { ensureData(); run(); };
  if (input.value) { ensureData(); }
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
      input.select();
    }
  });
})();
