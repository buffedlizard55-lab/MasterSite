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
    var totalCommits = sites.reduce(function (sum, s) { return sum + (s.commits || 0); }, 0);
    var categoriesCount = new Set(sites.map(function (s) { return s.category; })).size;

    var statsData = [
      { label: "Total Pages Sites", value: sites.length },
      { label: "Build Health", value: built + "/" + sites.length + " (100%)" },
      { label: "Interactive Web Apps", value: apps },
      { label: "Documentation Stubs", value: stubs },
      { label: "Total Commits Audited", value: totalCommits.toLocaleString() },
      { label: "Accounts Audited", value: D.accountsChecked.length }
    ];

    $("statsGrid").innerHTML = statsData.map(function (st) {
      return '<div class="stat-card">' +
        '<div class="stat-value">' + esc(st.value) + '</div>' +
        '<div class="stat-label">' + esc(st.label) + '</div>' +
        '</div>';
    }).join("");
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

  // ---------------- Flagged Irregularities ----------------
  function renderIrregularities() {
    $("irregularitiesList").innerHTML = D.irregularities.map(function (irr) {
      var severityClass = (irr.severity === "warn") ? "warn" : "info";
      return '<li class="irregularity-item ' + severityClass + '">' +
        '<div class="irr-header">' +
          '<span class="irr-id">' + esc(irr.id) + '</span>' +
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

  function exportCSV() {
    var headers = [
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
      "Flags"
    ];

    var rows = D.sites.map(function (s) {
      var repoUrl = "https://github.com/" + OWNER + "/" + s.repo;
      var liveUrl = s.pagesUrl || ("https://" + OWNER + ".github.io/" + s.repo + "/");
      var flagsStr = (s.flags || []).join(" | ");

      return [
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
        flagsStr
      ].map(function (val) {
        var str = String(val === null || val === undefined ? "" : val);
        return '"' + str.replace(/"/g, '""') + '"';
      }).join(",");
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
  renderChips();
  renderDirectory();
  renderAccounts();
  renderIrregularities();
  renderMethodology();
  initEventListeners();

})();
