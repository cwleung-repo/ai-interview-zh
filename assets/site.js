/* 交互：主题切换 / 搜索过滤 / 分类筛选 / 全部展开 */
(function () {
  "use strict";

  var root = document.documentElement;

  /* ---- theme ---- */
  function paintThemeIcon() {
    var icon = document.getElementById("themeIcon");
    if (!icon) return;
    var light = root.getAttribute("data-theme") === "light";
    icon.textContent = light ? "N" : "D";
    var btn = document.getElementById("themeToggle");
    if (btn) btn.setAttribute("aria-label", light ? "切换到暗色主题" : "切换到亮色主题");
  }
  function setTheme(mode) {
    root.setAttribute("data-theme", mode);
    try { localStorage.setItem("theme", mode); } catch (e) {}
    paintThemeIcon();
  window.dispatchEvent(new Event("themechange"));
  }
  var toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.onclick = function () {
      setTheme(root.getAttribute("data-theme") === "light" ? "dark" : "light");
    };
  }
  paintThemeIcon();

  /* ---- filtering ---- */
  var input = document.getElementById("filterInput");
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-filter-item]"));
  var countEl = document.getElementById("filterCount");
  var chips = Array.prototype.slice.call(document.querySelectorAll("input[name='cat']"));
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-group-block]"));

  function activeCat() {
    for (var i = 0; i < chips.length; i++) if (chips[i].checked) return chips[i].value;
    return "all";
  }

  function apply() {
    var q = (input && input.value ? input.value : "").trim().toLowerCase();
    var cat = activeCat();
    var shown = 0;
    items.forEach(function (el) {
      var hay = (el.getAttribute("data-search") || "").toLowerCase();
      var okText = !q || hay.indexOf(q) !== -1;
      var okCat = cat === "all" || el.getAttribute("data-cat") === cat;
      var ok = okText && okCat;
      el.hidden = !ok;
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      var any = g.querySelector("[data-filter-item]:not([hidden])");
      g.hidden = !any;
    });
    if (countEl) countEl.textContent = shown + " / " + items.length + " 项";
    var empty = document.getElementById("filterEmpty");
    if (empty) empty.hidden = shown !== 0;
  }

  if (input) {
    input.oninput = apply;
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input) {
        e.preventDefault();
        input.focus();
        input.select();
      }
      if (e.key === "Escape" && document.activeElement === input) {
        input.value = "";
        apply();
        input.blur();
      }
    });
  }
  chips.forEach(function (c) { c.onchange = apply; });
  apply();

  /* ---- expand / collapse all answers ---- */
  var openBtn = document.getElementById("expandAll");
  var closeBtn = document.getElementById("collapseAll");
  var answers = function () {
    return Array.prototype.slice.call(document.querySelectorAll("details.iv-answer, details.q-answer"));
  };
  if (openBtn) openBtn.onclick = function () { answers().forEach(function (d) { d.open = true; }); };
  if (closeBtn) closeBtn.onclick = function () { answers().forEach(function (d) { d.open = false; }); };

  /* ---- print: 展开所有答案，打印后恢复 ---- */
  var openedForPrint = [];
  window.addEventListener("beforeprint", function () {
    openedForPrint = answers().filter(function (d) { return !d.open; });
    openedForPrint.forEach(function (d) { d.open = true; });
  });
  window.addEventListener("afterprint", function () {
    openedForPrint.forEach(function (d) { d.open = false; });
    openedForPrint = [];
  });

  /* ---- copy page link ---- */
  var copyBtn = document.getElementById("copyLink");
  if (copyBtn) {
    copyBtn.onclick = function () {
      var url = window.location.href;
      function done() {
        copyBtn.textContent = "已复制链接";
        setTimeout(function () { copyBtn.textContent = "复制本页链接"; }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done, function () { window.prompt("复制链接", url); });
      } else {
        window.prompt("复制链接", url);
      }
    };
  }
})();
