(function () {
  "use strict";

  var D = window.MASTERDATA;
  var state = { q: "", category: "All", kind: "all", sort: "updated-desc" };

  var OWNER = D.owner;
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
  }

  function fmtDateShort(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
  }

  // ---------------- stats ----------------
  function renderStats() {
    var sites = D.sites;
    var apps = sites.filter(function (s) { return s.kind === "app"; }).length;
    var stubs = sites.length - apps;
    var built = sites.filter(function (s) { return s.pagesStatus === "built"; }).length;
    var cats = new Set(sites.map(function (s) { return s.category; })).size;
    var stats = [
      { n: sites.length, l: "GitHub Pages sites" },
      { n: built + "/" + sites.length, l: "Pages builds \u201cbuilt\u201d" },
      { n: apps, l: "Live sites with content" },
      { n: stubs, l: "README-only stubs" },
      { n: cats, l: "Categories" },
      { n: D.accountsChecked.length, l: "Accounts checked" }
    ];
    $("stats").innerHTML = stats.map(function (s) {
      return '<div class="stat"><b>' + esc(s.n) + "</b><span>" + esc(s.l) + "</span></div>";
    }).join("");
  }

  // ---------------- chips ----------------
  function renderChips() {
    var cats = ["All"].concat(Array.from(new Set(D.sites.map(function (s) { return s.category; }))).sort());
    $("categoryChips").innerHTML = cats.map(function (c) {
      var count = c === "All" ? D.sites.length : D.sites.filter(function (s) { return s.category === c; }).length;
      return '<button class="chip" data-cat="' + esc(c) + '" aria-pressed="' + (state.category === c) + '">' +
        esc(c) + " (" + count + ")</button>";
    }).join("");

    var kinds = [
      { id: "all", label: "All types", n: D.sites.length },
      { id: "app", label: "Live sites", n: D.sites.filter(function (s) { return s.kind === "app"; }).length },
      { id: "stub", label: "README stubs", n: D.sites.filter(function (s) { return s.kind === "stub"; }).length }
    ];
    $("kindChips").innerHTML = kinds.map(function (k) {
      return '<button class="chip" data-kind="' + k.id + '" aria-pressed="' + (state.kind === k.id) + '">' +
        esc(k.label) + " (" + k.n + ")</button>";
    }).join("");
  }

  // ---------------- cards ----------------
  function matches(s) {
    if (state.category !== "All" && s.category !== state.category) return false;
    if (state.kind !== "all" && s.kind !== state.kind) return false;
    if (state.q) {
      var hay = (s.title + " " + s.repo + " " + s.description + " " + s.category + " " + s.flags.join(" ")).toLowerCase();
      if (hay.indexOf(state.q.toLowerCase()) === -1) return false;
    }
    return true;
  }

  function sortSites(list) {
    var by = state.sort;
    return list.slice().sort(function (a, b) {
      if (by === "updated-desc") return (b.lastCommit || "").localeCompare(a.lastCommit || "");
      if (by === "created-desc") return b.created.localeCompare(a.created);
      if (by === "created-asc") return a.created.localeCompare(b.created);
      return a.repo.toLowerCase().localeCompare(b.repo.toLowerCase());
    });
  }

  function card(s) {
    var repoUrl = "https://github.com/" + OWNER + "/" + s.repo;
    var liveUrl = "https://" + OWNER + ".github.io/" + s.repo + "/";
    var apiUrl = "https://api.github.com/repos/" + OWNER + "/" + s.repo + "/pages";
    var settingsUrl = repoUrl + "/settings/pages";

    var badges =
      '<span class="badge built" title="GitHub Pages API status: ' + esc(s.pagesStatus) + ' · source: ' + esc(s.pagesSource) + '">Pages: ' + esc(s.pagesStatus) + "</span>" +
      (s.kind === "app"
        ? '<span class="badge app">Live site</span>'
        : '<span class="badge stub" title="Pages is built but only README content is served">README stub</span>') +
      (s.flags.length ? '<span class="badge flag" title="' + esc(s.flags.join(" | ")) + '">⚑ ' + s.flags.length + "</span>" : "");

    var flagsHtml = s.flags.length
      ? '<ul class="card-flags">' + s.flags.map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("") + "</ul>"
      : "";

    return (
      '<article class="card' + (s.repo === "MasterSite" ? " self" : "") + '">' +
      '<div class="card-top"><div><h3><a href="' + liveUrl + '" target="_blank" rel="noopener">' + esc(s.title) + "</a></h3>" +
      '<div class="repo-name">' + esc(s.repo) + "</div></div>" +
      '<div class="badges">' + badges + "</div></div>" +
      '<span class="cat">' + esc(s.category) + "</span>" +
      '<p class="desc">' + esc(s.description) + "</p>" +
      flagsHtml +
      '<div class="dates">' +
      "<span>Created <b>" + fmtDate(s.created) + "</b></span>" +
      '<span title="Newest commit on branch main">Last updated <b>' + fmtDate(s.lastCommit) + "</b></span>" +
      '<span title="Total commits on main (GitHub API)">' + s.commits + " commits</span>" +
      "</div>" +
      '<div class="card-links">' +
      '<a class="primary" href="' + liveUrl + '" target="_blank" rel="noopener">Visit site ↗</a>' +
      '<a href="' + repoUrl + '" target="_blank" rel="noopener">Repo</a>' +
      '<a href="' + apiUrl + '" target="_blank" rel="noopener" title="Official GitHub Pages API record (JSON)">Pages API</a>' +
      '<a href="' + settingsUrl + '" target="_blank" rel="noopener" title="GitHub Pages settings (requires repo admin login)">Pages settings</a>' +
      "</div></article>"
    );
  }

  function render() {
    var list = sortSites(D.sites.filter(matches));
    $("sites").innerHTML = list.length
      ? list.map(card).join("")
      : '<p class="empty">No sites match. Try clearing the search or filters.</p>';
    $("resultCount").textContent = "Showing " + list.length + " of " + D.sites.length + " sites" +
      (state.q ? ' for \u201c' + state.q + "\u201d" : "") + ".";
  }

  // ---------------- irregularities ----------------
  function renderIrr() {
    $("irrList").innerHTML = D.irregularities.map(function (i) {
      return '<li class="' + esc(i.severity) + '"><span class="irr-id">' + esc(i.id) + "</span><b>" +
        esc(i.title) + "</b><br>" + esc(i.detail) + "</li>";
    }).join("");
  }

  // ---------------- methodology ----------------
  function renderMethod() {
    $("methodSteps").innerHTML = D.methodology.steps.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("");
    $("methodCaveats").innerHTML = D.methodology.caveats.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("");
    $("genStamp").textContent = new Date(D.generated).toUTCString();
  }

  // ---------------- events ----------------
  $("search").addEventListener("input", function (e) { state.q = e.target.value.trim(); render(); });
  $("sort").addEventListener("change", function (e) { state.sort = e.target.value; render(); });
  $("categoryChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-cat]"); if (!b) return;
    state.category = b.getAttribute("data-cat"); renderChips(); render();
  });
  $("kindChips").addEventListener("click", function (e) {
    var b = e.target.closest("[data-kind]"); if (!b) return;
    state.kind = b.getAttribute("data-kind"); renderChips(); render();
  });

  renderStats();
  renderChips();
  render();
  renderIrr();
  renderMethod();
})();
