// pages/example.page.js
const { expect } = require('@playwright/test');

class ExamplePage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.header = page.locator('h1');
    this.getStartedButton = page.locator('text=Get started');
  }

  async goto() {
    await this.page.goto('https://playwright.dev/');
  }

  async clickGetStarted() {
    await this.getStartedButton.click();
  }

  async expectHeader(text) {
    await expect(this.header).toHaveText(text);
  }
}

module.exports = { ExamplePage };
