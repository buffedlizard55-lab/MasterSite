const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../data/sites.js'), 'utf8'), sandbox);
const snapshot = JSON.parse(JSON.stringify(sandbox.window.MASTERDATA));
const overlay = JSON.parse(fs.readFileSync(path.join(__dirname, '../tools/overlay.json'), 'utf8'));

test('executive summary renders every published site with official API links, accounts, and unreachable records', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/executive-summary.html');

  const rows = page.locator('#execTableBody tr');
  await expect(rows).toHaveCount(snapshot.sites.length);
  await expect(page.locator('#execResultCount')).toContainText(`Showing ${snapshot.sites.length} of ${snapshot.sites.length} websites`);
  await expect(page.locator('#execAuditDate')).toHaveText(snapshot.auditDate);

  // Audited accounts and unreachable records are visible with official API links.
  await expect(page.locator('#execAccountsGrid .account-card')).toHaveCount(snapshot.accountsChecked.length);
  await expect(page.locator('#execUnreachableList .unreachable-card')).toHaveCount(snapshot.unreachable.length);

  // Every prose-stale entry (including those with empty flags[]) must render as review, never healthy.
  const staleWithoutFlags = snapshot.sites.filter(s => s.proseStale && (!s.flags || s.flags.length === 0));
  expect(staleWithoutFlags.length).toBeGreaterThanOrEqual(1);
  for (const s of staleWithoutFlags) {
    const row = page.locator(`#execTableBody tr[data-repo="${s.repo}"]`);
    await expect(row.locator('.health-review')).toBeVisible();
    await expect(row.locator('.health-healthy')).toHaveCount(0);
  }

  // Excluded repositories never appear anywhere on the page.
  const bodyText = await page.locator('body').innerText();
  for (const name of overlay.excluded) {
    expect(bodyText).not.toContain(name);
  }
  expect(errors).toEqual([]);
});
