/* ══════════════════════════════════════════════════════════════════
   board_navdrawer.js —— 移动端「资料分类」抽屉（2026-10-30 新增）

   问题：<900px 时左侧 #siteNav 被 display:none 隐藏，且无任何替代入口，
        手机上无法在板块之间跳转，只能退回首页。

   方案：不复制 #siteNav 的内容（避免两份数据不同步），而是把同一个
        #siteNav 元素在窄屏下改为「覆盖式抽屉」定位，由顶栏按钮开合。

   行为：
     · 顶栏出现「☰ 资料分类」按钮（#navToggle）
     · 点击 → body.nav-open → 抽屉滑入 + 遮罩（#navScrim）出现
     · 点遮罩 / 按 Esc / 点抽屉里的链接 → 关闭
     · 视口放大到 >900px 时自动关闭并清理状态
     · 焦点在打开时移入抽屉，关闭时回到按钮（可访问性）
   ══════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var BREAKPOINT = 900;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var body = document.body;
    if (!body || !body.classList.contains("wiki-board")) return;

    var nav = document.getElementById("siteNav");
    if (!nav) return;

    // ── 注入按钮与遮罩（幂等：重复执行不重复插入）──────────
    var btn = document.getElementById("navToggle");
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "navToggle";
      btn.type = "button";
      btn.setAttribute("aria-controls", "siteNav");
      btn.setAttribute("aria-expanded", "false");
      btn.innerHTML = '<span aria-hidden="true">☰</span><span>资料分类</span>';

      // 插到顶栏面包屑之前（第一屏最显眼位置）
      var crumb = document.querySelector(".hd2-crumb");
      if (crumb && crumb.parentNode) {
        crumb.parentNode.insertBefore(btn, crumb);
      } else {
        var hd2 = document.querySelector(".hd2");
        if (hd2) hd2.insertBefore(btn, hd2.firstChild);
      }
    }

    var scrim = document.getElementById("navScrim");
    if (!scrim) {
      scrim = document.createElement("div");
      scrim.id = "navScrim";
      scrim.setAttribute("aria-hidden", "true");
      body.appendChild(scrim);
    }

    var isOpen = false;

    function openNav() {
      if (isOpen) return;
      isOpen = true;
      body.classList.add("nav-open");
      btn.setAttribute("aria-expanded", "true");
      // 焦点移入抽屉，方便键盘/读屏用户
      var first = nav.querySelector("a, button");
      if (first) {
        try { first.focus({ preventScroll: true }); } catch (e) { first.focus(); }
      }
    }

    function closeNav(refocus) {
      if (!isOpen) return;
      isOpen = false;
      body.classList.remove("nav-open");
      btn.setAttribute("aria-expanded", "false");
      if (refocus) {
        try { btn.focus({ preventScroll: true }); } catch (e) { btn.focus(); }
      }
    }

    btn.addEventListener("click", function () {
      if (isOpen) closeNav(true);
      else openNav();
    });

    scrim.addEventListener("click", function () {
      closeNav(true);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen) {
        closeNav(true);
      }
    });

    // 点抽屉里的链接后自动收起（跳转后页面重载，自然复位；
    // 同页锚点跳转时需要手动关）
    nav.addEventListener("click", function (e) {
      var t = e.target;
      if (t && t.closest && t.closest("a")) {
        closeNav(false);
      }
    });

    // 视口跨过断点时复位（桌面态不需要抽屉态）
    var mq = window.matchMedia("(max-width: " + (BREAKPOINT - 1) + "px)");
    var onMq = function () {
      if (!mq.matches) closeNav(false);
    };
    if (mq.addEventListener) mq.addEventListener("change", onMq);
    else if (mq.addListener) mq.addListener(onMq);

    // 供其他脚本查询
    window.WIKI_NAV_DRAWER = { open: openNav, close: closeNav, isOpen: function () { return isOpen; } };
  });
})();
