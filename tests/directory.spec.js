const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

// Read the committed snapshot, never the network, and do not hardcode site counts.
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../data/sites.js'), 'utf8'), sandbox);
const snapshot = JSON.parse(JSON.stringify(sandbox.window.MASTERDATA));
const overlay = JSON.parse(fs.readFileSync(path.join(__dirname, '../tools/overlay.json'), 'utf8'));
const cards = page => page.locator('#sitesGrid .site-card');
const rows = page => page.locator('#sitesTableBody tr');

// Synthetic edge cases are served only to the test browser. No fixture is ever
// written into the published dataset or passed off as verified repository data.
async function useFixture(page) {
  const data = JSON.parse(JSON.stringify(snapshot));
  const latest = '2026-09-21T00:00:00Z';
  const old = '2026-09-20T00:00:00Z';
  data.sites = ['Alpha', 'Beta', 'Gamma', 'Delta'].map((repo, i) => ({
    ...snapshot.sites[0], repo, title: repo,
    description: 'Synthetic test description & <text>',
    category: i < 2 ? 'Science & Tests' : 'Other',
    kind: i === 1 ? 'stub' : 'app',
    flags: i === 0 ? ['special test flag'] : [],
    defaultBranch: 'release',
    pagesStatus: ['built', 'building', 'errored', null][i],
    lastVerified: [latest, old, latest, null][i],
    verifiedAtSha: i === 3 ? null : 'a'.repeat(40),
    headSha: (i === 2 ? 'b' : 'a').repeat(40),
    proseStale: i === 2,
    lastCommit: `2026-09-${21 - i}T00:00:00Z`,
    commits: 10 + i
  }));
  data.counts.proseLatestPass = latest;
  data.counts.proseUnstamped = 1;
  await page.route('**/data/sites.js', route => route.fulfill({
    contentType: 'application/javascript', body: 'window.MASTERDATA = ' + JSON.stringify(data) + ';'
  }));
  return data;
}

test('committed snapshot renders without errors and preserves exclusion/accounting invariants', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(cards(page)).toHaveCount(snapshot.sites.length);
  await expect(rows(page)).toHaveCount(snapshot.sites.length);
  await expect(page.locator('#resultCount')).toContainText(`Showing ${snapshot.sites.length} of ${snapshot.sites.length}`);
  await expect(page.locator('#auditDatePill')).toHaveText(snapshot.auditDate);
  await expect(page.locator('#unreachableList .unreachable-card')).toHaveCount(snapshot.unreachable.length);
  expect(snapshot.counts.sites).toBe(snapshot.sites.length);
  expect(snapshot.sites.length + snapshot.counts.unlisted.length).toBe(snapshot.counts.pagesSites);
  expect(new Set(snapshot.sites.map(s => s.repo)).size).toBe(snapshot.sites.length);
  for (const name of overlay.excluded) {
    expect(snapshot.sites.some(s => s.repo === name)).toBe(false);
    expect(overlay.entries[name]).toBeUndefined();
  }
  for (const entry of Object.values(overlay.entries)) expect(typeof entry.description).toBe('string');
  await expect(page.locator('#verifyLegend')).toContainText('This page does not check live repository heads');
  expect(errors).toEqual([]);
});

test('URL restores combined filters, order and table layout after reload', async ({ page }) => {
  await useFixture(page);
  const query = new URLSearchParams({ q: 'test', category: 'Science & Tests', kind: 'app', prose: 'fresh', sort: 'name-desc', view: 'table' });
  await page.goto('/?' + query);
  await expect(rows(page)).toHaveCount(1);
  await expect(rows(page)).toContainText('Alpha');
  await expect(page.locator('#searchInput')).toHaveValue('test');
  await expect(page.locator('#proseSelect')).toHaveValue('fresh');
  await expect(page.locator('#sortSelect')).toHaveValue('name-desc');
  await expect(page.locator('[data-cat="Science & Tests"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('[data-kind="app"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#viewTableBtn')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#sitesGrid')).toBeHidden();
  await expect(page.locator('#sitesTableContainer')).toBeVisible();
  await page.reload();
  await expect(rows(page)).toHaveCount(1);
  await expect(rows(page)).toContainText('Alpha');
});

test('invalid enumerated parameters fall back safely and URL search is escaped', async ({ page }) => {
  await useFixture(page);
  const query = '<img src=x onerror="window.injected=true"> & 한글';
  await page.goto('/?' + new URLSearchParams({ q: query, category: 'missing', kind: 'bad', prose: '__proto__', sort: 'bad', view: 'bad' }));
  await expect(page.locator('#searchInput')).toHaveValue(query);
  await expect(page.locator('#resultCount')).toContainText(query);
  await expect(page.locator('#resultCount img')).toHaveCount(0);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
  await expect(page.locator('#proseSelect')).toHaveValue('all');
  await expect(page.locator('#sortSelect')).toHaveValue('updated-desc');
  await expect(page.locator('[data-cat="All"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('[data-kind="all"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#sitesGrid')).toBeVisible();
  await page.locator('#clearSearchBtn').click();
  await expect(cards(page)).toHaveCount(4);
  expect(new URL(page.url()).search).toBe('');
});

for (const [state, repo] of [['fresh', 'Alpha'], ['carried', 'Beta'], ['stale', 'Gamma'], ['unstamped', 'Delta']]) {
  test(`prose filter: ${state} agrees with badges and both layouts`, async ({ page }) => {
    await useFixture(page);
    await page.goto('/');
    await page.locator('#proseSelect').selectOption(state);
    await expect(cards(page)).toHaveCount(1);
    await expect(cards(page).locator('h3')).toHaveText(repo);
    await expect(rows(page)).toHaveCount(1);
    await expect(rows(page).locator('.table-repo')).toHaveText(repo);
    expect(new URL(page.url()).searchParams.get('prose')).toBe(state);
    await page.locator('#viewTableBtn').click();
    await expect(rows(page)).toBeVisible();
  });
}

test('reset clears every filter but preserves sort, layout, foreign parameters and anchor', async ({ page }) => {
  await useFixture(page);
  await page.goto('/?q=none&category=Other&kind=stub&prose=stale&sort=name-desc&view=table&source=bookmark#main-directory');
  await expect(page.locator('#sitesTableBody td')).toHaveAttribute('colspan', '9');
  await page.locator('#resetFiltersBtn').click();
  await expect(rows(page)).toHaveCount(4);
  await expect(rows(page).locator('.table-repo')).toHaveText(['Gamma', 'Delta', 'Beta', 'Alpha']);
  await expect(page.locator('#searchInput')).toBeFocused();
  await expect(page.locator('#resetFiltersBtn')).toBeDisabled();
  const url = new URL(page.url());
  expect(Object.fromEntries(url.searchParams)).toEqual({ sort: 'name-desc', view: 'table', source: 'bookmark' });
  expect(url.hash).toBe('#main-directory');
});

test('Back and Forward restore controls, results and view without per-keystroke history', async ({ page }) => {
  await useFixture(page);
  await page.goto('/');
  const historyLength = await page.evaluate(() => history.length);
  await page.locator('#searchInput').fill('test');
  expect(await page.evaluate(() => history.length)).toBe(historyLength);
  await page.locator('[data-cat="Science & Tests"]').click();
  await page.locator('[data-kind="stub"]').click();
  await page.locator('#viewTableBtn').click();
  await expect(rows(page)).toHaveCount(1);
  await page.goBack();
  await expect(page.locator('#sitesGrid')).toBeVisible();
  await expect(page.locator('#viewGridBtn')).toHaveAttribute('aria-pressed', 'true');
  await page.goBack();
  await expect(cards(page)).toHaveCount(2);
  await expect(page.locator('[data-kind="all"]')).toHaveAttribute('aria-pressed', 'true');
  await page.goForward();
  await expect(cards(page)).toHaveCount(1);
  await expect(page.locator('[data-kind="stub"]')).toHaveAttribute('aria-pressed', 'true');
});

test('search finds flags case-insensitively; chips retain keyboard focus', async ({ page }) => {
  await useFixture(page);
  await page.goto('/');
  await page.locator('#searchInput').fill('  SPECIAL TEST FLAG  ');
  await expect(cards(page)).toHaveCount(1);
  await expect(cards(page)).toContainText('Alpha');
  await page.locator('#clearSearchBtn').click();
  const chip = page.locator('[data-cat="Science & Tests"]');
  await chip.focus();
  await page.keyboard.press('Enter');
  await expect(chip).toBeFocused();
  await expect(chip).toHaveAttribute('aria-pressed', 'true');
  await expect(cards(page)).toHaveCount(2);
});

test('copy view link includes encoded state and has a manual fallback', async ({ page }) => {
  await useFixture(page);
  await page.goto('/');
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
      writeText: async text => { window.copiedText = text; }
    } });
  });
  await page.locator('[data-cat="Science & Tests"]').click();
  await page.locator('#shareViewBtn').click();
  expect(await page.evaluate(() => window.copiedText)).toBe(page.url());
  await expect(page.locator('#toast')).toHaveText('Copied link to this directory view!');
  await page.evaluate(() => {
    navigator.clipboard.writeText = () => Promise.reject(new Error('denied'));
  });
  const dialogPromise = page.waitForEvent('dialog');
  const clickPromise = page.locator('#shareViewBtn').click();
  const dialog = await dialogPromise;
  expect(dialog.type()).toBe('prompt');
  expect(dialog.defaultValue()).toBe(page.url());
  await dialog.dismiss();
  await clickPromise;
});

test('recorded build statuses and default branches are truthful in both layouts', async ({ page }) => {
  await useFixture(page);
  await page.goto('/?sort=name-asc');
  const expectedStatuses = ['built', 'building', 'unknown', 'errored'];
  for (const [i, status] of expectedStatuses.entries()) {
    const card = cards(page).nth(i);
    const badge = card.locator('.card-badges .tag-badge').first();
    await expect(badge).toContainText(status);
    await expect(badge).toHaveClass(status === 'built' ? 'tag-badge built' : 'tag-badge flagged');
    await expect(card).toContainText('commits on release');
    await expect(rows(page).nth(i).locator('td').nth(3)).toContainText(status);
  }
  await expect(page.locator('#verifyLegend')).toContainText('repository at the snapshot');
  await expect(page.locator('#verifyLegend')).not.toContainText('right now');
});

for (const view of ['grid', 'table']) {
  test(`inspector is keyboard-modal and returns focus in ${view} view`, async ({ page }) => {
    await useFixture(page);
    await page.goto('/?view=' + view);
    const opener = page.locator(view === 'grid' ? '#sitesGrid [data-inspect]' : '#sitesTableBody [data-inspect]').first();
    await opener.focus();
    await page.keyboard.press('Enter');
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await expect(page.locator('#closeModalBtn')).toBeFocused();
    await expect(dialog).toContainText('matches recorded head — not proof of accuracy');
    await page.keyboard.press('Shift+Tab');
    await expect(page.locator('#modalLiveLink')).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.locator('#closeModalBtn')).toBeFocused();
    // Native dialogs make the background inert, even for programmatic focus.
    await page.locator('#searchInput').evaluate(el => el.focus());
    await expect(page.locator('#closeModalBtn')).toBeFocused();
    for (let i = 0; i < 16; i++) {
      await page.keyboard.press('Tab');
      expect(await page.evaluate(() => document.querySelector('#inspectorModal').contains(document.activeElement))).toBe(true);
    }
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
    await expect(page.locator('body')).not.toHaveClass(/inspector-open/);
    await page.keyboard.press('Enter');
    await page.locator('#closeModalBtn').click();
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
    await page.keyboard.press('Enter');
    await page.locator('#inspectorModal').click({ position: { x: 3, y: 3 } });
    await expect(dialog).toBeHidden();
  });
}

test('JSON and CSV remain complete ledgers, independent of active filters', async ({ page }) => {
  await page.goto('/?q=definitely-no-matching-site');
  await expect(cards(page)).toHaveCount(0);
  for (const format of ['Json', 'Csv']) {
    await page.locator('#exportMenuBtn').click();
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#export' + format + 'Btn').click();
    const download = await downloadPromise;
    const content = fs.readFileSync(await download.path(), 'utf8');
    if (format === 'Json') {
      expect(JSON.parse(content)).toEqual(snapshot);
    } else {
      expect(content).toContain('Description_Verification_State');
      for (const site of snapshot.sites) expect(content).toContain('"listed","' + site.repo + '"');
      for (const site of snapshot.unreachable) {
        expect(content).toContain('"unreachable-404 (' + site.retiredAt + ')","' + site.repo + '"');
      }
      for (const name of overlay.excluded) expect(content).not.toContain(',"' + name + '",');
    }
  }
});

test('export disclosure closes on Escape and returns focus', async ({ page }) => {
  await page.goto('/');
  await page.locator('#exportMenuBtn').click();
  await page.locator('#exportJsonBtn').focus();
  await page.keyboard.press('Escape');
  await expect(page.locator('#exportMenu')).toBeHidden();
  await expect(page.locator('#exportMenuBtn')).toBeFocused();
  await expect(page.locator('#exportMenuBtn')).toHaveAttribute('aria-expanded', 'false');
});

test('review controls and cards fit narrow screens', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await expect(page.locator('#proseSelect')).toBeVisible();
  await expect(page.locator('#shareViewBtn')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.locator('#proseSelect').selectOption('stale');
  await expect(cards(page)).toHaveCount(snapshot.sites.filter(s => s.proseStale && s.lastVerified && s.verifiedAtSha).length);
});
