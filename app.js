(function () {
  "use strict";

  var D = window.MASTERDATA;
  if (!D || !D.sites) {
    console.error("MasterSite: MASTERDATA object is missing or invalid.");
    return;
  }

  var OWNER = D.owner || "buffedlizard55-lab";
  var state = {
    q: "",
    category: "All",
    kind: "all",
    sort: "updated-desc",
    view: "grid" // "grid" or "table"
  };

  var $ = function (id) {
    return document.getElementById(id);
  };

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

  // ---- Description-prose verification helpers -------------------------------
  // Two independent signals, because one is not enough (IRR-50):
  //   lastVerified  — WHEN the prose was last re-read against the repository.
  //   verifiedAtSha — WHICH COMMIT it was read against, compared with the live
  //                   head SHA so staleness is computed rather than guessed.
  function proseIsFresh(s) {
    var latest = (D.counts && D.counts.proseLatestPass) || null;
    return !!(latest && s.lastVerified === latest);
  }

  function proseState(s) {
    if (!s.lastVerified || !s.verifiedAtSha) return "unstamped";
    return s.proseStale ? "stale" : (proseIsFresh(s) ? "fresh" : "carried");
  }

  function proseFreshClass(s) {
    return "prose-" + proseState(s);
  }

  function proseBasis(s) {
    var sha = s.verifiedAtSha
      ? " Prose read against commit " + s.verifiedAtSha +
        (s.proseStale
          ? "; the repository's default branch is now at " + (s.headSha || "?") +
            ", so this description is provably behind it and must be re-read."
          : "; that is still the repository's latest commit, so the prose matches the bytes it was read from.")
      : "";
    if (!s.lastVerified) {
      return "No prose-verification stamp: this description has never been re-read against the repository's own files." + sha;
    }
    return (proseIsFresh(s) ? "Re-read in the latest pass. " : "Carried forward from an earlier pass. ") +
           (s.verifiedBasis || "") + sha;
  }

  var PROSE_LABEL = {
    fresh:   "Prose re-read",
    carried: "Prose carried",
    stale:   "Prose behind repo",
    unstamped: "Prose unstamped"
  };

  function proseBadge(s) {
    var st = proseState(s);
    var when = s.lastVerified ? " " + esc(fmtDate(s.lastVerified)) : "";
    return '<span class="tag-badge ' + (st === "fresh" ? "prose-fresh" : st) +
           '" title="' + esc(proseBasis(s)) + '">' +
           (st === "stale" ? "⚠ " : "") + PROSE_LABEL[st] + when + '</span>';
  }

  function showToast(msg) {
    var toast = $("toast");
    toast.textContent = msg;
    toast.style.display = "block";
    clearTimeout(toast._timer);
    toast._timer = setTimeout(function () {
      toast.style.display = "none";
    }, 2800);
  }

  function copyText(text, successMsg) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        showToast(successMsg || "Copied to clipboard!");
      }).catch(function () {
        prompt("Copy text manually:", text);
      });
    } else {
      prompt("Copy text manually:", text);
    }
  }

  // ---------------- Stats Grid ----------------
  function renderStats() {
    var sites = D.sites;
    var apps = sites.filter(function (s) { return s.kind === "app"; }).length;
    var stubs = sites.filter(function (s) { return s.kind === "stub"; }).length;
    var built = sites.filter(function (s) { return s.pagesStatus === "built"; }).length;
    var other = sites.length - built;
    var totalCommits = sites.reduce(function (sum, s) { return sum + (s.commits || 0); }, 0);

    var health = (other === 0)
      ? built + "/" + sites.length + " built"
      : built + "/" + sites.length + " built · " + other + " other";

    // Descriptions re-read against the repository's own files in the latest pass.
    // Computed from the data so it can never disagree with the per-entry stamps.
    var latestPass = (D.counts && D.counts.proseLatestPass) || null;
    var reRead = latestPass
      ? sites.filter(function (s) { return s.lastVerified === latestPass; }).length
      : 0;

    var statsData = [
      { label: "Total Pages Sites", value: sites.length },
      { label: "Build Health", value: health },
      { label: "Interactive Web Apps", value: apps },
      { label: "Documentation Stubs", value: stubs },
      { label: "Total Commits Audited", value: totalCommits.toLocaleString() },
      { label: "Accounts Audited", value: D.accountsChecked.length }
    ];

    if (latestPass) {
      statsData.push({
        label: "Descriptions Re-Read This Pass",
        value: reRead + " / " + sites.length
      });
    }

    // Mechanically detected: the commit the prose was read against is no
    // longer the repository's head. Computed, never asserted by hand.
    var staleProse = sites.filter(function (s) { return s.proseStale; }).length;
    statsData.push({
      label: "Prose Behind Its Repo",
      value: staleProse + " / " + sites.length,
      warn: staleProse > 0
    });

    var unreachable = D.unreachable || [];
    if (unreachable.length) {
      statsData.push({ label: "Unreachable (Retired)", value: unreachable.length });
    }

    $("statsGrid").innerHTML = statsData.map(function (st) {
      return '<div class="stat-card' + (st.warn ? ' stat-warn' : '') + '">' +
        '<div class="stat-value">' + esc(st.value) + '</div>' +
        '<div class="stat-label">' + esc(st.label) + '</div>' +
        '</div>';
    }).join("");
  }

  // ---------------- Verification Legend ----------------
  // "Verified" means two different things on this site, and conflating them is how a
  // description goes stale while every number still checks out. This states both, from
  // the dataset, so a reader always knows which one they are looking at.
  function renderVerifyLegend() {
    var el = $("verifyLegend");
    if (!el) return;
    var c = D.counts || {};
    var latestPass = c.proseLatestPass || null;
    if (!latestPass) { el.style.display = "none"; return; }

    var total = D.sites.length;
    var reRead = D.sites.filter(function (s) { return s.lastVerified === latestPass; }).length;
    var carried = total - reRead;
    var unstamped = c.proseUnstamped || 0;
    var stale = D.sites.filter(function (s) { return s.proseStale; }).length;

    el.innerHTML =
      '<strong>Two kinds of “verified”.</strong> ' +
      '<em>API fields</em> — every timestamp, commit SHA, commit count, Pages status, build source and ' +
      'size on all ' + total + ' entries — are re-read from <code>api.github.com</code> on every build ' +
      '(this dataset: <strong>' + esc(fmtDateTime(D.generated)) + '</strong>). ' +
      '<em>Description prose</em> is a separate question: it is re-read against each repository’s own ' +
      'files, and each entry carries a <code>lastVerified</code> stamp, a <code>verifiedBasis</code> ' +
      'string saying what was read, and a <code>verifiedAtSha</code> — the commit the prose was read ' +
      'against. In the latest pass <strong>' + reRead + '</strong> of ' + total + ' descriptions were ' +
      're-read; <strong>' + carried + '</strong> were carried forward and say why that is safe' +
      (unstamped ? '; <span class="legend-warn">' + unstamped + ' are unstamped</span>' : '') + '. ' +
      'Because each stamp names a commit, staleness is <em>computed</em> rather than assumed: ' +
      (stale
        ? '<span class="legend-warn">' + stale + ' entr' + (stale === 1 ? 'y is' : 'ies are') +
          ' provably behind ' + (stale === 1 ? 'its' : 'their') + ' repository right now</span> — the ' +
          'prose was read against a commit that is no longer the default branch’s head, so ' +
          (stale === 1 ? 'it needs' : 'they need') + ' re-reading. '
        : '<strong>0</strong> entries are behind their repository — every description was read against ' +
          'the commit its repository still points at. ') +
      'A timestamp alone cannot show this: one repository in this audit moved 60 seconds after being ' +
      'stamped (IRR-50). Sort by “Description Verified (Stalest first)” to review the oldest prose first.';
  }

  // ---------------- Filter Chips ----------------
  function renderChips() {
    var allCategories = ["All"].concat(
      Array.from(new Set(D.sites.map(function (s) { return s.category; }))).sort()
    );

    $("categoryChips").innerHTML = allCategories.map(function (cat) {
      var count = (cat === "All")
        ? D.sites.length
        : D.sites.filter(function (s) { return s.category === cat; }).length;
      var isPressed = state.category === cat;
      return '<button class="chip" data-cat="' + esc(cat) + '" aria-pressed="' + isPressed + '">' +
        esc(cat) + ' <span class="chip-count">' + count + '</span></button>';
    }).join("");

    var kinds = [
      { id: "all", label: "All Types", count: D.sites.length },
      { id: "app", label: "Interactive Apps", count: D.sites.filter(function (s) { return s.kind === "app"; }).length },
      { id: "stub", label: "Doc / README Stubs", count: D.sites.filter(function (s) { return s.kind === "stub"; }).length }
    ];

    $("kindChips").innerHTML = kinds.map(function (k) {
      var isPressed = state.kind === k.id;
      return '<button class="chip" data-kind="' + esc(k.id) + '" aria-pressed="' + isPressed + '">' +
        esc(k.label) + ' <span class="chip-count">' + k.count + '</span></button>';
    }).join("");
  }

  // ---------------- Filtering and Sorting ----------------
  function filterSites() {
    var q = state.q.toLowerCase().trim();
    return D.sites.filter(function (s) {
      if (state.category !== "All" && s.category !== state.category) return false;
      if (state.kind !== "all" && s.kind !== state.kind) return false;
      if (q) {
        var flagsText = (s.flags || []).join(" ");
        var hay = [s.title, s.repo, s.description, s.category, s.kind, flagsText].join(" ").toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function sortSites(list) {
    var by = state.sort;
    return list.slice().sort(function (a, b) {
      if (by === "updated-desc") return (b.lastCommit || "").localeCompare(a.lastCommit || "");
      if (by === "updated-asc") return (a.lastCommit || "").localeCompare(b.lastCommit || "");
      if (by === "created-desc") return (b.created || "").localeCompare(a.created || "");
      if (by === "created-asc") return (a.created || "").localeCompare(b.created || "");
      if (by === "name-asc") return (a.title || a.repo).toLowerCase().localeCompare((b.title || b.repo).toLowerCase());
      if (by === "name-desc") return (b.title || b.repo).toLowerCase().localeCompare((a.title || a.repo).toLowerCase());
      if (by === "commits-desc") return (b.commits || 0) - (a.commits || 0);
      // A null stamp sorts as the stalest possible value, so "stalest first" puts
      // never-re-read prose at the top of the review queue.
      if (by === "verified-asc") return (a.lastVerified || "").localeCompare(b.lastVerified || "");
      if (by === "verified-desc") return (b.lastVerified || "").localeCompare(a.lastVerified || "");
      return 0;
    });
  }

  // ---------------- Site Card (Grid View) ----------------
  function renderCard(s) {
    var repoUrl = "https://github.com/" + OWNER + "/" + s.repo;
    var liveUrl = s.pagesUrl || ("https://" + OWNER + ".github.io/" + s.repo + "/");
    var apiUrl = "https://api.github.com/repos/" + OWNER + "/" + s.repo + "/pages";
    var settingsUrl = repoUrl + "/settings/pages";
    var isSelf = (s.repo === "MasterSite");

    var typeBadge = (s.kind === "app")
      ? '<span class="tag-badge app">Interactive App</span>'
      : '<span class="tag-badge stub">Doc Stub</span>';

    var builtBadge = '<span class="tag-badge built" title="GitHub Pages build status: ' + esc(s.pagesStatus) + ' · Source: ' + esc(s.pagesSource) + '">Built (' + esc(s.pagesSource) + ')</span>';

    var flagBadge = (s.flags && s.flags.length > 0)
      ? '<span class="tag-badge flagged" title="' + esc(s.flags.join(" | ")) + '">⚑ Notice</span>'
      : '';

    var flagsBox = (s.flags && s.flags.length > 0)
      ? '<div class="card-flags-box"><ul>' + s.flags.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join("") + '</ul></div>'
      : '';

    return '<article class="site-card' + (isSelf ? ' is-self' : '') + '">' +
      '<div class="card-header">' +
        '<div class="card-title-group">' +
          '<h3><a href="' + esc(liveUrl) + '" target="_blank" rel="noopener">' + esc(s.title) + '</a></h3>' +
          '<div class="repo-badge">' +
            '<span>' + esc(s.repo) + '</span>' +
            '<button class="copy-icon-btn" data-copy="' + esc(s.repo) + '" title="Copy repository name" aria-label="Copy repository name">' +
              '<svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/></svg>' +
            '</button>' +
          '</div>' +
        '</div>' +
        '<div class="card-badges">' +
          builtBadge +
          typeBadge +
          proseBadge(s) +
          flagBadge +
        '</div>' +
      '</div>' +
      '<span class="category-tag">' + esc(s.category) + '</span>' +
      '<p class="card-desc">' + esc(s.description) + '</p>' +
      flagsBox +
      '<div class="card-metrics">' +
        '<div class="metric-item">' +
          '<span class="metric-label">Created (UTC)</span>' +
          '<span class="metric-value" title="Repo created: ' + esc(s.created) + ' · 1st commit: ' + esc(s.firstCommit) + ' (' + esc(s.firstCommitSha) + ')">' + fmtDate(s.created) + '</span>' +
        '</div>' +
        '<div class="metric-item">' +
          '<span class="metric-label">Last Updated (UTC)</span>' +
          '<span class="metric-value" title="Latest commit: ' + esc(s.lastCommit) + ' (' + esc(s.lastCommitSha) + ')">' + fmtDate(s.lastCommit) + '</span>' +
        '</div>' +
        '<div class="metric-item">' +
          '<span class="metric-label">Activity Total</span>' +
          '<span class="metric-value">' + (s.commits || 0) + ' commits on main</span>' +
        '</div>' +
        '<div class="metric-item">' +
          '<span class="metric-label">Deployment Path</span>' +
          '<span class="metric-value">' + esc(s.pagesSource) + '</span>' +
        '</div>' +
        '<div class="metric-item">' +
          '<span class="metric-label">Description Verified</span>' +
          '<span class="metric-value ' + proseFreshClass(s) + '" title="' + esc(proseBasis(s)) + '">' +
            (s.lastVerified ? fmtDate(s.lastVerified) : 'never stamped') +
          '</span>' +
        '</div>' +
      '</div>' +
      '<div class="card-actions">' +
        '<a class="action-btn primary" href="' + esc(liveUrl) + '" target="_blank" rel="noopener">Visit Site ↗</a>' +
        '<a class="action-btn" href="' + esc(repoUrl) + '" target="_blank" rel="noopener">Repo</a>' +
        '<a class="action-btn" href="' + esc(apiUrl) + '" target="_blank" rel="noopener" title="Official GitHub Pages API record (JSON)">API JSON</a>' +
        '<a class="action-btn" href="' + esc(settingsUrl) + '" target="_blank" rel="noopener" title="GitHub Pages settings (requires admin access)">Settings</a>' +
        '<button class="action-btn inspect-btn" data-inspect="' + esc(s.repo) + '" title="View verified telemetry and raw JSON">Inspect</button>' +
      '</div>' +
    '</article>';
  }

  // ---------------- Table Row (Table View) ----------------
  function renderTableRow(s, index) {
    var repoUrl = "https://github.com/" + OWNER + "/" + s.repo;
    var liveUrl = s.pagesUrl || ("https://" + OWNER + ".github.io/" + s.repo + "/");
    var apiUrl = "https://api.github.com/repos/" + OWNER + "/" + s.repo + "/pages";

    var typeClass = (s.kind === "app") ? "app" : "stub";
    var typeText = (s.kind === "app") ? "Live App" : "README Stub";

    return '<tr>' +
      '<td>' + (index + 1) + '</td>' +
      '<td class="table-name-cell">' +
        '<strong><a href="' + esc(liveUrl) + '" target="_blank" rel="noopener">' + esc(s.title) + '</a></strong>' +
        '<span class="table-repo">' + esc(s.repo) + '</span>' +
      '</td>' +
      '<td><span class="category-tag">' + esc(s.category) + '</span></td>' +
      '<td>' +
        '<span class="tag-badge ' + typeClass + '">' + typeText + '</span> ' +
        '<span class="tag-badge built">' + esc(s.pagesStatus) + '</span>' +
      '</td>' +
      '<td title="' + esc(s.created) + '">' + fmtDate(s.created) + '</td>' +
      '<td title="' + esc(s.lastCommit) + ' (' + esc(s.lastCommitSha) + ')">' + fmtDate(s.lastCommit) + '</td>' +
      '<td class="' + proseFreshClass(s) + '" title="' + esc(proseBasis(s)) + '">' +
        (s.lastVerified ? fmtDate(s.lastVerified) : '—') +
      '</td>' +
      '<td><strong>' + (s.commits || 0) + '</strong></td>' +
      '<td>' +
        '<div class="table-actions-cell">' +
          '<a class="action-btn primary" href="' + esc(liveUrl) + '" target="_blank" rel="noopener" style="padding:4px 8px;font-size:11.5px;">Live ↗</a>' +
          '<a class="action-btn" href="' + esc(repoUrl) + '" target="_blank" rel="noopener" style="padding:4px 8px;font-size:11.5px;">Repo</a>' +
          '<a class="action-btn" href="' + esc(apiUrl) + '" target="_blank" rel="noopener" style="padding:4px 8px;font-size:11.5px;">API</a>' +
          '<button class="action-btn inspect-btn" data-inspect="' + esc(s.repo) + '" style="padding:4px 8px;font-size:11.5px;">Inspect</button>' +
        '</div>' +
      '</td>' +
    '</tr>';
  }

  // ---------------- Master Directory Render ----------------
  function renderDirectory() {
    var filtered = filterSites();
    var list = sortSites(filtered);

    // Update Result Count text
    var countText = "Showing " + list.length + " of " + D.sites.length + " verified sites";
    if (state.q) {
      countText += ' matching "' + esc(state.q) + '"';
    }
    if (state.category !== "All") {
      countText += " in " + esc(state.category);
    }
    if (state.kind !== "all") {
      countText += " (" + (state.kind === "app" ? "Interactive Apps only" : "Doc Stubs only") + ")";
    }
    $("resultCount").innerHTML = countText + ".";

    // Render Grid
    if (list.length === 0) {
      $("sitesGrid").innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:48px 20px;color:var(--muted);background:var(--card);border:1px dashed var(--line);border-radius:var(--radius-lg);">' +
        '<h3>No matching sites found</h3><p>Try resetting the search query or selecting "All" categories.</p></div>';
      $("sitesTableBody").innerHTML = '<tr><td colspan="8" style="text-align:center;padding:32px;color:var(--muted);">No matching sites found.</td></tr>';
      return;
    }

    $("sitesGrid").innerHTML = list.map(renderCard).join("");
    $("sitesTableBody").innerHTML = list.map(function (s, idx) {
      return renderTableRow(s, idx);
    }).join("");
  }

  // ---------------- Accounts Breakdown ----------------
  function renderAccounts() {
    $("accountsGrid").innerHTML = D.accountsChecked.map(function (acc) {
      return '<div class="account-card">' +
        '<div class="account-card-header">' +
          '<div class="account-name"><a href="' + esc(acc.profile) + '" target="_blank" rel="noopener">' + esc(acc.login) + '</a></div>' +
          '<span class="tag-badge ' + (acc.publicRepos > 0 ? 'app' : 'stub') + '">' + (acc.publicRepos > 0 ? acc.publicRepos + ' Repos' : '0 Repos') + '</span>' +
        '</div>' +
        '<div class="account-meta">' +
          '<span>Created: <strong>' + fmtDate(acc.accountCreated) + '</strong></span> · ' +
          '<span>Pages Sites: <strong>' + acc.pagesSites + '</strong></span>' +
        '</div>' +
        '<p class="account-note">' + esc(acc.note) + '</p>' +
        '<div style="margin-top:6px;">' +
          '<a class="action-btn" href="' + esc(acc.apiRepos) + '" target="_blank" rel="noopener" style="font-size:12px;padding:4px 8px;">View Official Repos API JSON ↗</a>' +
        '</div>' +
      '</div>';
    }).join("");
  }

  // ---------------- Unreachable / Retired Entries ----------------
  function renderUnreachable() {
    var list = D.unreachable || [];
    var section = $("unreachable-section");
    if (!list.length || !section) return;
    section.hidden = false;

    $("unreachableList").innerHTML = list.map(function (u) {
      var repoUrl = "https://github.com/" + OWNER + "/" + u.repo;
      var apiUrl = "https://api.github.com/repos/" + OWNER + "/" + u.repo;
      var evidence = (u.retiredEvidence || []).map(function (e) {
        var isUrl = /^https?:\/\//.test(e);
        var label = esc(e.split(" — ")[0]);
        return isUrl
          ? '<li><a href="' + esc(e.split(" — ")[0]) + '" target="_blank" rel="noopener">' + label + '</a>' +
            '<span class="ev-note">' + esc(e.split(" — ").slice(1).join(" — ")) + '</span></li>'
          : '<li>' + esc(e) + '</li>';
      }).join("");

      return '<article class="unreachable-card">' +
        '<div class="unreachable-head">' +
          '<h3>' + esc(u.title || u.repo) + '</h3>' +
          '<span class="tag-badge unreachable">HTTP 404 — Removed Upstream</span>' +
        '</div>' +
        '<p class="unreachable-reason">' + esc(u.retiredReason || "") + '</p>' +
        '<dl class="unreachable-metrics">' +
          '<div><dt>Last verified commit</dt><dd>' + esc(u.lastCommitSha) + ' · ' + fmtDateTime(u.lastCommit) + '</dd></div>' +
          '<div><dt>Created (UTC)</dt><dd>' + fmtDateTime(u.created) + '</dd></div>' +
          '<div><dt>Commits at retirement</dt><dd>' + (u.commits || 0) + '</dd></div>' +
          '<div><dt>Retired on</dt><dd>' + esc(u.retiredAt || "—") + '</dd></div>' +
        '</dl>' +
        '<div class="unreachable-desc">' + esc(u.description || "") + '</div>' +
        '<div class="unreachable-evidence"><strong>Reproduce the 404:</strong><ul>' + evidence + '</ul></div>' +
        '<div class="card-actions">' +
          '<a class="action-btn" href="' + esc(apiUrl) + '" target="_blank" rel="noopener">Repo API (404) ↗</a>' +
          '<a class="action-btn" href="' + esc(repoUrl) + '" target="_blank" rel="noopener">Repo Page ↗</a>' +
        '</div>' +
      '</article>';
    }).join("");
  }

  // ---------------- Flagged Irregularities ----------------
  function renderIrregularities() {
    var sevOrder = { critical: 0, warn: 1, info: 2 };
    function sevRank(sev) {
      var r = sevOrder[sev];
      return (r === undefined) ? 9 : r;
    }
    var items = (D.irregularities || []).slice().sort(function (a, b) {
      return sevRank(a.severity) - sevRank(b.severity);
    });

    $("irregularitiesList").innerHTML = items.map(function (irr) {
      var severityClass = (irr.severity === "warn" || irr.severity === "critical") ? irr.severity : "info";
      var sevLabel = irr.severity === "critical" ? "CRITICAL" : (irr.severity === "warn" ? "WARN" : "INFO");
      return '<li class="irregularity-item ' + severityClass + '">' +
        '<div class="irr-header">' +
          '<span class="irr-id">' + esc(irr.id) + '</span>' +
          '<span class="irr-sev ' + severityClass + '">' + sevLabel + '</span>' +
          '<span class="irr-title">' + esc(irr.title) + '</span>' +
        '</div>' +
        '<p class="irr-detail">' + esc(irr.detail) + '</p>' +
      '</li>';
    }).join("");
  }

  // ---------------- Methodology & Sources ----------------
  function renderMethodology() {
    $("methodSteps").innerHTML = D.methodology.steps.map(function (st) {
      return '<li>' + esc(st) + '</li>';
    }).join("");

    $("methodCaveats").innerHTML = D.methodology.caveats.map(function (c) {
      return '<li>' + esc(c) + '</li>';
    }).join("");

    $("genStamp").textContent = fmtDateTime(D.generated);

    // Audit date is data-driven so it can never drift from the generated dataset.
    var audit = (D.auditDate || (D.generated || "").slice(0, 10) || "—");
    if ($("auditDatePill")) $("auditDatePill").textContent = audit;
    if ($("accountsAuditDate")) $("accountsAuditDate").textContent = audit;
  }

  // ---------------- Site Inspector Modal ----------------
  function openInspector(repoName) {
    var site = D.sites.find(function (s) { return s.repo === repoName; });
    if (!site) return;

    var repoUrl = "https://github.com/" + OWNER + "/" + site.repo;
    var liveUrl = site.pagesUrl || ("https://" + OWNER + ".github.io/" + site.repo + "/");
    var apiUrl = "https://api.github.com/repos/" + OWNER + "/" + site.repo + "/pages";
    var settingsUrl = repoUrl + "/settings/pages";

    $("modalCategory").textContent = site.category;
    $("modalTitle").textContent = site.title;
    $("modalRepoId").textContent = site.repo;
    $("modalLiveLink").href = liveUrl;

    var flagsHtml = (site.flags && site.flags.length > 0)
      ? '<div class="card-flags-box" style="margin-bottom:12px;"><strong>Audit Flags:</strong><ul>' + site.flags.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join("") + '</ul></div>'
      : '<p style="color:var(--green);font-size:13px;margin:0 0 12px;">✓ No irregularities flagged for this repository.</p>';

    $("modalBody").innerHTML =
      flagsHtml +
      '<table class="modal-table">' +
        '<tbody>' +
          '<tr><td>Description</td><td>' + esc(site.description) + '</td></tr>' +
          '<tr><td>GitHub Pages Status</td><td><strong>' + esc(site.pagesStatus) + '</strong> (Source: ' + esc(site.pagesSource) + ')</td></tr>' +
          '<tr><td>Site Type</td><td>' + (site.kind === "app" ? "Interactive Web Application" : "Documentation / README Stub") + '</td></tr>' +
          '<tr><td>Repo Created (UTC)</td><td>' + fmtDateTime(site.created) + '</td></tr>' +
          '<tr><td>First Commit (UTC)</td><td>' + fmtDateTime(site.firstCommit) + ' (SHA: ' + esc(site.firstCommitSha) + ')</td></tr>' +
          '<tr><td>Latest Commit (UTC)</td><td>' + fmtDateTime(site.lastCommit) + ' (SHA: ' + esc(site.lastCommitSha) + ')</td></tr>' +
          '<tr><td>Last Push to Repo (UTC)</td><td>' + fmtDateTime(site.pushedAt) + '</td></tr>' +
          '<tr><td>Description Last Verified (UTC)</td><td><span class="' + proseFreshClass(site) + '">' +
            (site.lastVerified ? fmtDateTime(site.lastVerified) : 'never stamped') + '</span>' +
            (proseIsFresh(site) ? ' — re-read in the latest pass' : ' — carried forward') + '</td></tr>' +
          '<tr><td>Prose read against commit</td><td>' +
            (site.verifiedAtSha
              ? '<code>' + esc(site.verifiedAtSha) + '</code> · repository default branch is now ' +
                '<code>' + esc(site.headSha || '?') + '</code> · ' +
                (site.proseStale
                  ? '<span class="prose-stale"><strong>behind the repository — description must be re-read</strong></span>'
                  : '<span class="prose-fresh">matches — prose describes the current bytes</span>')
              : 'not stamped') + '</td></tr>' +
          '<tr><td>What “verified” means here</td><td>' + esc(site.verifiedBasis ||
            'No basis recorded. This entry’s description prose has not been re-read against the repository’s own files; only its API-derived fields were re-checked.') + '</td></tr>' +
          '<tr><td>Total Main Commits</td><td>' + (site.commits || 0) + '</td></tr>' +
          '<tr><td>Default Branch</td><td>' + esc(site.defaultBranch) + '</td></tr>' +
          '<tr><td>Repository Size</td><td>' + (site.sizeKb || 0) + ' KB</td></tr>' +
          '<tr><td>Live URL</td><td><a href="' + esc(liveUrl) + '" target="_blank" rel="noopener">' + esc(liveUrl) + '</a></td></tr>' +
          '<tr><td>Repo URL</td><td><a href="' + esc(repoUrl) + '" target="_blank" rel="noopener">' + esc(repoUrl) + '</a></td></tr>' +
          '<tr><td>Official Pages API</td><td><a href="' + esc(apiUrl) + '" target="_blank" rel="noopener">' + esc(apiUrl) + '</a></td></tr>' +
          '<tr><td>Pages Settings</td><td><a href="' + esc(settingsUrl) + '" target="_blank" rel="noopener">' + esc(settingsUrl) + '</a></td></tr>' +
        '</tbody>' +
      '</table>' +
      '<div style="margin-top:10px;">' +
        '<div style="font-size:12px;font-weight:700;text-transform:uppercase;color:var(--muted);margin-bottom:4px;">Verified MasterData JSON Record:</div>' +
        '<pre class="raw-json-block" id="modalRawJson">' + esc(JSON.stringify(site, null, 2)) + '</pre>' +
      '</div>';

    $("inspectorModal").style.display = "flex";
  }

  function closeInspector() {
    $("inspectorModal").style.display = "none";
  }

  // ---------------- Export Data ----------------
  function downloadFile(content, fileName, mimeType) {
    var blob = new Blob([content], { type: mimeType });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function exportJSON() {
    var jsonStr = JSON.stringify(D, null, 2);
    downloadFile(jsonStr, "buffedlizard55-lab-github-pages-masterlist.json", "application/json");
    showToast("Downloaded MasterData JSON!");
  }

  function csvCell(val) {
    var str = String(val === null || val === undefined ? "" : val);
    return '"' + str.replace(/"/g, '""') + '"';
  }

  function csvRow(s, status) {
    var repoUrl = "https://github.com/" + OWNER + "/" + s.repo;
    var liveUrl = s.pagesUrl || ("https://" + OWNER + ".github.io/" + s.repo + "/");
    return [
      status,
      s.repo,
      s.title,
      s.category,
      s.kind,
      s.pagesStatus,
      s.pagesSource,
      liveUrl,
      repoUrl,
      s.created,
      s.lastCommit,
      s.lastCommitSha,
      s.commits,
      s.description,
      (s.flags || []).join(" | "),
      s.lastVerified,
      proseState(s),
      s.verifiedAtSha,
      s.headSha,
      s.proseStale ? "yes" : "no",
      s.verifiedBasis
    ].map(csvCell).join(",");
  }

  function exportCSV() {
    var headers = [
      "Status",
      "Repository",
      "Title",
      "Category",
      "Kind",
      "Pages_Status",
      "Pages_Source",
      "Live_URL",
      "Repo_URL",
      "Created_UTC",
      "Last_Commit_UTC",
      "Last_Commit_SHA",
      "Total_Commits",
      "Description",
      "Flags",
      "Description_Last_Verified_UTC",
      "Description_Verification_State",
      "Prose_Read_At_SHA",
      "Repo_Head_SHA",
      "Prose_Behind_Repo",
      "Description_Verification_Basis"
    ];

    var rows = D.sites.map(function (s) { return csvRow(s, "listed"); });

    // Retired / unreachable entries are exported too, clearly marked, so the CSV
    // stays a complete ledger rather than a silently pruned list.
    (D.unreachable || []).forEach(function (u) {
      rows.push(csvRow(u, "unreachable-404 (" + (u.retiredAt || "") + ")"));
    });

    var csvContent = headers.join(",") + "\n" + rows.join("\n");
    downloadFile(csvContent, "buffedlizard55-lab-github-pages-masterlist.csv", "text/csv;charset=utf-8;");
    showToast("Downloaded MasterData CSV!");
  }

  // ---------------- Event Listeners ----------------
  function initEventListeners() {
    // Search input
    $("searchInput").addEventListener("input", function (e) {
      state.q = e.target.value;
      $("clearSearchBtn").style.display = state.q ? "block" : "none";
      renderDirectory();
    });

    $("clearSearchBtn").addEventListener("click", function () {
      $("searchInput").value = "";
      state.q = "";
      $("clearSearchBtn").style.display = "none";
      $("searchInput").focus();
      renderDirectory();
    });

    // Sort select
    $("sortSelect").addEventListener("change", function (e) {
      state.sort = e.target.value;
      renderDirectory();
    });

    // View toggles
    $("viewGridBtn").addEventListener("click", function () {
      state.view = "grid";
      $("viewGridBtn").classList.add("active");
      $("viewGridBtn").setAttribute("aria-pressed", "true");
      $("viewTableBtn").classList.remove("active");
      $("viewTableBtn").setAttribute("aria-pressed", "false");
      $("sitesGrid").style.display = "grid";
      $("sitesTableContainer").style.display = "none";
    });

    $("viewTableBtn").addEventListener("click", function () {
      state.view = "table";
      $("viewTableBtn").classList.add("active");
      $("viewTableBtn").setAttribute("aria-pressed", "true");
      $("viewGridBtn").classList.remove("active");
      $("viewGridBtn").setAttribute("aria-pressed", "false");
      $("sitesGrid").style.display = "none";
      $("sitesTableContainer").style.display = "block";
    });

    // Category chips
    $("categoryChips").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-cat]");
      if (!btn) return;
      state.category = btn.getAttribute("data-cat");
      renderChips();
      renderDirectory();
    });

    // Kind chips
    $("kindChips").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-kind]");
      if (!btn) return;
      state.kind = btn.getAttribute("data-kind");
      renderChips();
      renderDirectory();
    });

    // Delegation for Inspect & Copy buttons in Grid and Table
    document.addEventListener("click", function (e) {
      var inspectBtn = e.target.closest("[data-inspect]");
      if (inspectBtn) {
        var repoName = inspectBtn.getAttribute("data-inspect");
        openInspector(repoName);
        return;
      }

      var copyBtn = e.target.closest("[data-copy]");
      if (copyBtn) {
        var text = copyBtn.getAttribute("data-copy");
        copyText(text, 'Copied "' + text + '" to clipboard!');
        return;
      }
    });

    // Export dropdown menu
    $("exportMenuBtn").addEventListener("click", function (e) {
      e.stopPropagation();
      var menu = $("exportMenu");
      var isOpen = menu.style.display === "flex";
      menu.style.display = isOpen ? "none" : "flex";
      $("exportMenuBtn").setAttribute("aria-expanded", !isOpen);
    });

    document.addEventListener("click", function () {
      $("exportMenu").style.display = "none";
      $("exportMenuBtn").setAttribute("aria-expanded", "false");
    });

    $("exportJsonBtn").addEventListener("click", function () {
      exportJSON();
    });

    $("exportCsvBtn").addEventListener("click", function () {
      exportCSV();
    });

    // Modal close & copy
    $("closeModalBtn").addEventListener("click", closeInspector);
    $("inspectorModal").addEventListener("click", function (e) {
      if (e.target === $("inspectorModal")) {
        closeInspector();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && $("inspectorModal").style.display === "flex") {
        closeInspector();
      }
    });

    $("copyJsonBtn").addEventListener("click", function () {
      var raw = $("modalRawJson").textContent;
      copyText(raw, "Copied JSON to clipboard!");
    });
  }

  // ---------------- Initialization ----------------
  renderStats();
  renderVerifyLegend();
  renderChips();
  renderDirectory();
  renderUnreachable();
  renderAccounts();
  renderIrregularities();
  renderMethodology();
  initEventListeners();

})();
