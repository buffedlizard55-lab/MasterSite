(function () {
  "use strict";

  var D = window.MASTERDATA;
  if (!D || !D.sites) {
    document.getElementById("execTableBody").innerHTML =
      '<tr class="exec-empty"><td colspan="9">Could not load site data (data/sites.js missing or invalid).</td></tr>';
    return;
  }

  var OWNER = D.owner || "buffedlizard55-lab";
  var API_BASE = "https://api.github.com";
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

  function shortSha(sha) {
    if (!sha) return "";
    return String(sha).slice(0, 7);
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
  function repoApiUrl(s) {
    return API_BASE + "/repos/" + OWNER + "/" + s.repo;
  }
  function pagesApiUrl(s) {
    return repoApiUrl(s) + "/pages";
  }
  function commitsApiUrl(s) {
    return repoApiUrl(s) + "/commits?sha=" + encodeURIComponent(s.defaultBranch || "main");
  }
  function recordJsonUrl(s) {
    return "data/sites/" + OWNER + "__" + s.repo + ".json";
  }

  // Build the complete list of review reasons from recorded flags, description
  // provenance staleness (PROSE-STALE), missing stamps, and non-built Pages status.
  function reviewReasonsOf(s) {
    var reasons = (s.flags || []).slice();
    if (!s.lastVerified || !s.verifiedAtSha) {
      reasons.push("Missing description verification stamp (lastVerified / verifiedAtSha).");
    } else if (s.proseStale) {
      reasons.push(
        "PROSE-STALE: description read at " + shortSha(s.verifiedAtSha) +
        " is behind recorded head " + (shortSha(s.headSha) || "unknown") +
        " — re-read source files before treating prose as current."
      );
    }
    var status = s.pagesStatus || "unknown";
    if (status !== "built") {
      reasons.push("Pages API status is '" + status + "' at snapshot (not 'built').");
    }
    return reasons;
  }

  // Review state summarizes recorded per-entry flags, description provenance
  // staleness, build status, and whether an HTML entry point exists; it is not a
  // live uptime check.
  function healthOf(s) {
    if (reviewReasonsOf(s).length > 0) return "review";
    if (s.kind === "stub") return "stub";
    return "healthy";
  }

  function healthBadge(s) {
    var reasons = reviewReasonsOf(s);
    var h = healthOf(s);
    if (h === "review") {
      var listItems = reasons.map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
      return '<span class="health health-review" title="' + esc(reasons.join(" | ")) + '">⚠ Review (' + reasons.length + ")</span>" +
        '<ul class="exec-flag-reasons">' + listItems + "</ul>";
    }
    if (h === "stub") {
      return '<span class="health health-stub" title="No index.html at the recorded Pages source path; the published root may render a README.">📝 Stub</span>';
    }
    return '<span class="health health-healthy" title="Description stamp matches recorded head, Pages status is built, and no per-entry audit flags are recorded; this is not an uptime or user-activity check.">✓ No flags</span>';
  }

  // ---------------- KPIs ----------------
  function renderKpis() {
    var sites = D.sites;
    var apps = sites.filter(function (s) { return s.kind === "app"; }).length;
    var stubs = sites.length - apps;
    var built = sites.filter(function (s) { return s.pagesStatus === "built"; }).length;
    var commits = sites.reduce(function (sum, s) { return sum + (s.commits || 0); }, 0);
    var needReview = sites.filter(function (s) { return healthOf(s) === "review"; }).length;
    var staleCount = sites.filter(function (s) { return Boolean(s.proseStale); }).length;

    var ref = new Date(D.generated || Date.now()).getTime();
    var fresh7 = sites.filter(function (s) {
      return s.lastCommit && (ref - new Date(s.lastCommit).getTime()) < 7 * 86400000;
    }).length;

    var cards = [
      { value: String(sites.length), label: "Sites listed", sub: "as of " + fmtDate(D.generated) },
      { value: apps + " / " + stubs, label: "HTML sites / Stubs", sub: built + " of " + sites.length + " built" },
      { value: String(fresh7), label: "Recent commits (7 days)", sub: "relative to snapshot date" },
      { value: String(needReview), label: "Need review", sub: staleCount + " prose-stale · flags/status" },
      { value: commits.toLocaleString(), label: "Total commits", sub: "across all sites" }
    ];

    $("execKpis").innerHTML = cards.map(function (c) {
      return '<div class="stat-card"><div class="stat-value">' + esc(c.value) + "</div>" +
        '<div class="stat-label">' + esc(c.label) + "</div>" +
        '<div class="stat-sub">' + esc(c.sub) + "</div></div>";
    }).join("");

    var auditDateText = D.auditDate || (D.generated || "").slice(0, 10) || "—";
    $("execAuditDate").textContent = auditDateText;
    $("execGenerated").textContent = fmtDateTime(D.generated);
    $("execGenerated2").textContent = fmtDateTime(D.generated);
    $("execGenStamp").textContent = fmtDateTime(D.generated);
    if ($("execAccountsDate")) {
      $("execAccountsDate").textContent = fmtDateTime(D.generated);
    }
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
        var hay = [
          s.title,
          s.repo,
          s.description,
          s.category,
          (reviewReasonsOf(s) || []).join(" ")
        ].join(" ").toLowerCase();
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
    var vSha = shortSha(s.verifiedAtSha);
    var hSha = shortSha(s.headSha);
    var proseStampHtml = vSha
      ? '<div class="exec-sha exec-prose-stamp' + (s.proseStale ? " stale" : "") + '" title="Description read ' + esc(fmtDateTime(s.lastVerified)) + ' at commit ' + esc(s.verifiedAtSha) + (s.proseStale ? ' (behind recorded head ' + esc(hSha || s.headSha) + ')' : ' (matches recorded head)') + '">' +
          'prose: ' + esc(vSha) + (s.proseStale ? " ⚠ stale" : " ✓") +
        "</div>"
      : '<div class="exec-sha exec-prose-stamp stale" title="Missing description verification stamp">prose: unstamped ⚠</div>';

    return '<tr data-repo="' + esc(s.repo) + '">' +
      // 1 — Website name (+ repo id + one-line description)
      '<td data-label="Website">' +
        '<div class="exec-site-name"><a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(s.title) + "</a></div>" +
        '<div class="exec-repo">' + esc(s.repo) + "</div>" +
        (desc ? '<div class="exec-desc" title="' + esc(s.description) + '">' + esc(desc) + "</div>" : "") +
      "</td>" +
      // 2 — Direct link + official API review links
      '<td data-label="Live link">' +
        '<a class="exec-visit" href="' + esc(url) + '" target="_blank" rel="noopener" title="' + esc(url) + '">Visit ↗</a>' +
        '<div class="exec-source-links" aria-label="Official review sources for ' + esc(s.repo) + '">' +
          '<a class="exec-repo-link" href="' + esc(repoUrl(s)) + '" target="_blank" rel="noopener" title="GitHub repository">Repo</a>' +
          '<a class="exec-api-link" href="' + esc(repoApiUrl(s)) + '" target="_blank" rel="noopener" title="Official GitHub REST API repository endpoint">Repo API</a>' +
          '<a class="exec-api-link" href="' + esc(pagesApiUrl(s)) + '" target="_blank" rel="noopener" title="Official GitHub REST API Pages endpoint">Pages API</a>' +
          '<a class="exec-api-link" href="' + esc(commitsApiUrl(s)) + '" target="_blank" rel="noopener" title="Official GitHub REST API default-branch commits endpoint">Commits API</a>' +
          '<a class="exec-api-link" href="' + esc(recordJsonUrl(s)) + '" target="_blank" rel="noopener" title="Per-site JSON record in data/sites/">JSON</a>' +
        "</div>" +
      "</td>" +
      // 3 — Last default-branch commit (not last site use) + prose stamp
      '<td data-label="Last commit"><div class="exec-updated" title="Newest committer timestamp on the default branch: ' + esc(fmtDateTime(s.lastCommit)) + '. GitHub does not expose last site use.">' +
        '<div class="exec-updated-date">' + esc(fmtDate(s.lastCommit)) + "</div>" +
        '<div class="exec-updated-ago ' + age.cls + '">' + esc(age.text) + "</div>" +
        (s.lastCommitSha ? '<div class="exec-sha">head: ' + esc(shortSha(s.lastCommitSha)) + "</div>" : "") +
        proseStampHtml +
      "</div></td>" +
      // 4 — Category
      '<td data-label="Category"><span class="exec-pill">' + esc(s.category) + "</span></td>" +
      // 5 — Type
      '<td data-label="Type">' + (s.kind === "app"
        ? '<span class="exec-pill app" title="index.html exists at the recorded Pages path">HTML</span>'
        : '<span class="exec-pill stub" title="No index.html at the recorded Pages path">Stub</span>') + "</td>" +
      // 6 — Build
      '<td data-label="Build" title="Recorded Pages status at snapshot · Source: ' + esc(s.pagesSource) + '">' +
        '<span class="exec-pill ' + (built ? "built" : "notbuilt") + '">' + esc(s.pagesStatus || "unknown") + "</span></td>" +
      // 7 — Commits
      '<td data-label="Commits" class="exec-commits">' + esc(String(s.commits || 0)) + "</td>" +
      // 8 — Created
      '<td data-label="Created"><span class="exec-created" title="Repository created_at: ' + esc(fmtDateTime(s.created)) + (s.firstCommit ? " · First commit: " + esc(fmtDateTime(s.firstCommit)) : "") + '">' + esc(fmtDate(s.created)) + "</span>" +
        (s.firstCommitSha ? '<div class="exec-sha">init: ' + esc(shortSha(s.firstCommitSha)) + "</div>" : "") +
      "</td>" +
      // 9 — Review state
      '<td data-label="Review state">' + healthBadge(s) + "</td>" +
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

  // ---------------- Audited Accounts & Unreachable Records ----------------
  function renderAccounts() {
    var grid = $("execAccountsGrid");
    if (!grid) return;
    var accounts = D.accountsChecked || [];
    grid.innerHTML = accounts.map(function (a) {
      var userApi = API_BASE + "/users/" + a.login;
      var reposApi = (a.apiRepos || (userApi + "/repos")) + "?per_page=100";
      return '<div class="account-card" data-account="' + esc(a.login) + '">' +
        '<div class="account-header">' +
          '<a class="account-login" href="' + esc(a.profile) + '" target="_blank" rel="noopener"><strong>' + esc(a.login) + "</strong> ↗</a>" +
          '<span class="exec-pill ' + (a.publicRepos > 0 ? "built" : "") + '">' + esc(String(a.publicRepos || 0)) + " public repos · " + esc(String(a.pagesSites || 0)) + " Pages</span>" +
        "</div>" +
        '<p class="account-note">' + esc(a.note || "") + "</p>" +
        '<div class="exec-source-links">' +
          '<a class="exec-api-link" href="' + esc(a.profile) + '" target="_blank" rel="noopener">GitHub Profile</a>' +
          '<a class="exec-api-link" href="' + esc(userApi) + '" target="_blank" rel="noopener">User API</a>' +
          '<a class="exec-api-link" href="' + esc(reposApi) + '" target="_blank" rel="noopener">Repos API</a>' +
        "</div>" +
      "</div>";
    }).join("");
  }

  function renderUnreachable() {
    var section = $("exec-unreachable-section");
    var container = $("execUnreachableList");
    if (!section || !container) return;
    var items = D.unreachable || [];
    if (!items.length) {
      section.hidden = true;
      container.innerHTML = "";
      return;
    }
    section.hidden = false;
    container.innerHTML = items.map(function (u) {
      var apiRepo = API_BASE + "/repos/" + OWNER + "/" + u.repo;
      var apiPages = apiRepo + "/pages";
      return '<div class="unreachable-card" data-unreachable-repo="' + esc(u.repo) + '">' +
        '<div class="unreachable-header">' +
          '<strong>' + esc(u.title || u.repo) + "</strong> " +
          '<span class="exec-repo">(' + esc(u.repo) + ")</span> " +
          '<span class="health health-review">HTTP 404 since ' + esc(u.retiredAt || "snapshot") + "</span>" +
        "</div>" +
        '<p class="unreachable-desc">' + esc(u.description || "") + "</p>" +
        '<div class="unreachable-meta">' +
          "Created: " + esc(fmtDate(u.created)) +
          " · Last recorded commit: " + esc(fmtDate(u.lastCommit)) +
          (u.lastCommitSha ? " (" + esc(shortSha(u.lastCommitSha)) + ")" : "") +
          " · Commits: " + esc(String(u.commits || 0)) +
          " · Last Pages status: " + esc(u.pagesStatus || "unknown") +
        "</div>" +
        '<div class="exec-source-links">' +
          '<a class="exec-api-link" href="' + esc(apiRepo) + '" target="_blank" rel="noopener">Repo API (404 check)</a>' +
          '<a class="exec-api-link" href="' + esc(apiPages) + '" target="_blank" rel="noopener">Pages API (404 check)</a>' +
          '<a class="exec-api-link" href="https://github.com/buffedlizard55-lab/MasterSite/blob/main/OWNER-DECISIONS.md" target="_blank" rel="noopener">Owner Decision Record</a>' +
        "</div>" +
      "</div>";
    }).join("");
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
  renderAccounts();
  renderUnreachable();
})();
