// tests/example.spec.js
const { test, expect } = require('@playwright/test');
const { ExamplePage } = require('../pages/example.page');

test.describe('Playwright Example Page', () => {
  test('should display the correct header and navigate', async ({ page }) => {
    const examplePage = new ExamplePage(page);
    await examplePage.goto();
    await examplePage.expectHeader('Playwright enables reliable end-to-end testing for modern web apps.');
    await examplePage.clickGetStarted();
    await expect(page).toHaveURL(/.*docs\/intro/);
  });
});
