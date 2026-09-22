const { defineConfig, devices } = require('@playwright/test');

// An existing local browser can be used in sandboxes that block browser downloads.
const chromiumLaunch = process.env.CHROMIUM_PATH ? {
  executablePath: process.env.CHROMIUM_PATH,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle', '--use-angle=swiftshader']
} : {};

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 2,
  reporter: 'list',
  use: {
    baseURL: process.env.TEST_BASE_URL || 'http://127.0.0.1:4173',
    trace: 'retain-on-failure',
    reducedMotion: 'reduce'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], launchOptions: chromiumLaunch } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chromium', use: { ...devices['Pixel 7'], launchOptions: chromiumLaunch } }
  ],
  // Arena uses a separately managed server via TEST_BASE_URL. Normal local/CI
  // runs get an ephemeral static server owned and cleaned up by the test runner.
  webServer: process.env.TEST_BASE_URL ? undefined : {
    command: 'python3 -m http.server 4173 --bind 0.0.0.0',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: !process.env.CI
  }
});
