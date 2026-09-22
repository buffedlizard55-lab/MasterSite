(function () {
  "use strict";

  var D = window.MASTERDATA;
  if (!D || !D.sites) {
    document.getElementById("execTableBody").innerHTML =
      '<tr class="exec-empty"><td colspan="9">Could not load site data (data/sites.js missing or invalid).</td></tr>';
    return;
  }

  var OWNER = D.owner || "buffedlizard55-lab";
  var state = { q: "", category: "All", health: "all", sort: "updated-desc" };

  function $(id) { return document.getElementById(id); }

  function esc(s) {
    if (s === null || s === undefined) return "";
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
  }

  function fmtDateTime(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toISOString().replace("T", " ").replace("Z", " UTC");
  }

  // Plain-English age measured against the snapshot, so every reader sees the
  // same value regardless of when they open the page.
  function ageInfo(iso) {
    if (!iso) return { text: "unknown", cls: "older" };
    var then = new Date(iso).getTime();
    var ref = new Date(D.generated || Date.now()).getTime();
    var days = Math.max(0, Math.floor((ref - then) / 86400000));
    if (days < 1) return { text: "today", cls: "fresh" };
    if (days === 1) return { text: "yesterday", cls: "fresh" };
    if (days < 7) return { text: days + " days ago", cls: "fresh" };
    if (days < 30) {
      var w = Math.floor(days / 7);
      return { text: w === 1 ? "1 week ago" : w + " weeks ago", cls: "recent" };
    }
    if (days < 365) {
      var m = Math.floor(days / 30);
      return { text: m === 1 ? "1 month ago" : m + " months ago", cls: "older" };
    }
    var y = Math.floor(days / 365);
    return { text: y === 1 ? "1 year ago" : y + " years ago", cls: "older" };
  }

  function liveUrl(s) {
    return s.pagesUrl || ("https://" + OWNER + ".github.io/" + s.repo + "/");
  }
  function repoUrl(s) {
    return "https://github.com/" + OWNER + "/" + s.repo;
  }

  // Health answers "should I worry?" — flags first, then stub, else healthy.
  function healthOf(s) {
    if (s.flags && s.flags.length > 0) return "review";
    if (s.kind === "stub") return "stub";
    return "healthy";
  }

  function healthBadge(s) {
    var h = healthOf(s);
    if (h === "review") {
      var reasons = (s.flags || []).map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
      return '<span class="health health-review" title="' + esc((s.flags || []).join(" | ")) + '">⚠ Review (' + s.flags.length + ")</span>" +
        '<ul class="exec-flag-reasons">' + reasons + "</ul>";
    }
    if (h === "stub") {
      return '<span class="health health-stub" title="Documentation / README placeholder — no interactive site yet.">📝 Stub</span>';
    }
    return '<span class="health health-healthy" title="No audit flags; a real published app.">✓ Healthy</span>';
  }

  // ---------------- KPIs ----------------
  function renderKpis() {
    var sites = D.sites;
    var apps = sites.filter(function (s) { return s.kind === "app"; }).length;
    var stubs = sites.length - apps;
    var built = sites.filter(function (s) { return s.pagesStatus === "built"; }).length;
    var commits = sites.reduce(function (sum, s) { return sum + (s.commits || 0); }, 0);
    var needReview = sites.filter(function (s) { return healthOf(s) === "review"; }).length;

    var ref = new Date(D.generated || Date.now()).getTime();
    var fresh7 = sites.filter(function (s) {
      return s.lastCommit && (ref - new Date(s.lastCommit).getTime()) < 7 * 86400000;
    }).length;

    var cards = [
      { value: String(sites.length), label: "Websites tracked", sub: "as of " + fmtDate(D.generated) },
      { value: apps + " / " + stubs, label: "Live apps / Stubs", sub: built + " of " + sites.length + " built" },
      { value: String(fresh7), label: "Updated in last 7 days", sub: "of snapshot date" },
      { value: String(needReview), label: "Need review", sub: needReview === 0 ? "nothing flagged" : "have audit flags" },
      { value: commits.toLocaleString(), label: "Total commits", sub: "across all sites" }
    ];

    $("execKpis").innerHTML = cards.map(function (c) {
      return '<div class="stat-card"><div class="stat-value">' + esc(c.value) + "</div>" +
        '<div class="stat-label">' + esc(c.label) + "</div>" +
        '<div class="stat-sub">' + esc(c.sub) + "</div></div>";
    }).join("");

    $("execAuditDate").textContent = D.auditDate || (D.generated || "").slice(0, 10) || "—";
    $("execGenerated").textContent = fmtDateTime(D.generated);
    $("execGenerated2").textContent = fmtDateTime(D.generated);
    $("execGenStamp").textContent = fmtDateTime(D.generated);
  }

  // ---------------- Filters ----------------
  function renderCategoryOptions() {
    var cats = Array.from(new Set(D.sites.map(function (s) { return s.category; }))).sort();
    $("execCategory").innerHTML = ["All"].concat(cats).map(function (c) {
      var n = c === "All" ? D.sites.length : D.sites.filter(function (s) { return s.category === c; }).length;
      return '<option value="' + esc(c) + '">' + esc(c === "All" ? "All categories" : c) + " (" + n + ")</option>";
    }).join("");
  }

  function filtered() {
    var q = state.q.toLowerCase().trim();
    return D.sites.filter(function (s) {
      if (state.category !== "All" && s.category !== state.category) return false;
      if (state.health !== "all" && healthOf(s) !== state.health) return false;
      if (q) {
        var hay = [s.title, s.repo, s.description, s.category].join(" ").toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function sorted(list) {
    return list.slice().sort(function (a, b) {
      switch (state.sort) {
        case "updated-asc": return (a.lastCommit || "").localeCompare(b.lastCommit || "");
        case "updated-desc": return (b.lastCommit || "").localeCompare(a.lastCommit || "");
        case "name-asc": return (a.title || a.repo).toLowerCase().localeCompare((b.title || b.repo).toLowerCase());
        case "name-desc": return (b.title || b.repo).toLowerCase().localeCompare((a.title || a.repo).toLowerCase());
        case "commits-desc": return (b.commits || 0) - (a.commits || 0);
        case "commits-asc": return (a.commits || 0) - (b.commits || 0);
        case "created-desc": return (b.created || "").localeCompare(a.created || "");
        case "created-asc": return (a.created || "").localeCompare(b.created || "");
        default: return 0;
      }
    });
  }

  // ---------------- Table ----------------
  function rowHtml(s) {
    var url = liveUrl(s);
    var age = ageInfo(s.lastCommit);
    var desc = (s.description || "").length > 160
      ? s.description.slice(0, 157).replace(/\s+\S*$/, "") + "…"
      : (s.description || "");
    var built = (s.pagesStatus || "unknown") === "built";

    return "<tr>" +
      // 1 — Website name (+ repo id + one-line description)
      '<td data-label="Website">' +
        '<div class="exec-site-name"><a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(s.title) + "</a></div>" +
        '<div class="exec-repo">' + esc(s.repo) + "</div>" +
        (desc ? '<div class="exec-desc" title="' + esc(s.description) + '">' + esc(desc) + "</div>" : "") +
      "</td>" +
      // 2 — Direct link
      '<td data-label="Live link">' +
        '<a class="exec-visit" href="' + esc(url) + '" target="_blank" rel="noopener" title="' + esc(url) + '">Visit ↗</a><br>' +
        '<a class="exec-repo-link" href="' + esc(repoUrl(s)) + '" target="_blank" rel="noopener">Repo</a>' +
      "</td>" +
      // 3 — Last updated
      '<td data-label="Last updated"><div class="exec-updated" title="' + esc(fmtDateTime(s.lastCommit)) + '">' +
        '<div class="exec-updated-date">' + esc(fmtDate(s.lastCommit)) + "</div>" +
        '<div class="exec-updated-ago ' + age.cls + '">' + esc(age.text) + "</div>" +
        (s.lastCommitSha ? '<div class="exec-sha">' + esc(s.lastCommitSha) + "</div>" : "") +
      "</div></td>" +
      // 4 — Category
      '<td data-label="Category"><span class="exec-pill">' + esc(s.category) + "</span></td>" +
      // 5 — Type
      '<td data-label="Type">' + (s.kind === "app"
        ? '<span class="exec-pill app">App</span>'
        : '<span class="exec-pill stub">Stub</span>') + "</td>" +
      // 6 — Build
      '<td data-label="Build" title="Recorded Pages status at snapshot · Source: ' + esc(s.pagesSource) + '">' +
        '<span class="exec-pill ' + (built ? "built" : "notbuilt") + '">' + esc(s.pagesStatus || "unknown") + "</span></td>" +
      // 7 — Commits
      '<td data-label="Commits" class="exec-commits">' + esc(String(s.commits || 0)) + "</td>" +
      // 8 — Created
      '<td data-label="Created"><span class="exec-created" title="' + esc(fmtDateTime(s.created)) + '">' + esc(fmtDate(s.created)) + "</span></td>" +
      // 9 — Health
      '<td data-label="Health">' + healthBadge(s) + "</td>" +
    "</tr>";
  }

  function renderTable() {
    var list = sorted(filtered());
    $("execResultCount").textContent =
      "Showing " + list.length + " of " + D.sites.length + " websites" +
      (state.q ? ' matching "' + state.q + '"' : "") +
      (state.category !== "All" ? " in " + state.category : "") +
      (state.health !== "all" ? " · " + state.health : "") + ".";
    $("execTableBody").innerHTML = list.length
      ? list.map(rowHtml).join("")
      : '<tr class="exec-empty"><td colspan="9"><strong>No matching websites.</strong><br>Clear the search or change the filters.</td></tr>';
  }

  // ---------------- Events ----------------
  $("execSearch").addEventListener("input", function (e) {
    state.q = e.target.value;
    $("execClearSearch").style.display = state.q ? "block" : "none";
    renderTable();
  });
  $("execClearSearch").addEventListener("click", function () {
    state.q = "";
    $("execSearch").value = "";
    $("execClearSearch").style.display = "none";
    renderTable();
    $("execSearch").focus();
  });
  $("execCategory").addEventListener("change", function (e) {
    state.category = e.target.value;
    renderTable();
  });
  $("execHealth").addEventListener("change", function (e) {
    state.health = e.target.value;
    renderTable();
  });
  $("execSort").addEventListener("change", function (e) {
    state.sort = e.target.value;
    renderTable();
  });

  // ---------------- Init ----------------
  renderKpis();
  renderCategoryOptions();
  renderTable();
})();
