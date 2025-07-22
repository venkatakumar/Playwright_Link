// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  /* Maximum time one test can run for. */
  timeout: 30 * 1000,
  expect: {
    timeout: 5000
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  /* Configure projects for major browsers */
  projects: [
    {
      name: 'API Tests',
      use: {
        baseURL: 'https://reqres.in/api',
        extraHTTPHeaders: {
          'Accept': 'application/json',
          'x-api-key': 'reqres-free-v1'
        }
      },
    },
  ],
});
