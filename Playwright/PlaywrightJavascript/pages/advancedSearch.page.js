// pages/advancedSearch.page.js
const { expect } = require('@playwright/test');

class AdvancedSearchPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.advancedTab = page.getByRole('link', { name: 'Advanced search' })
    this.referenceInput = page.getByRole('textbox', { name: 'Reference number-input' });
    this.searchButton = page.getByRole('button', { name: 'Search', exact: true });
    this.results = page.getByRole('link');
  }

  async goto() {
    await this.page.goto('https://planningregister.planningsystemni.gov.uk/simple-search');
    await this.advancedTab.click();
  }

  async searchByReference(ref) {
    await this.referenceInput.click();
    await this.referenceInput.fill(ref);
    await this.searchButton.click();
  }

  async expectResults() {
    await expect(this.results).toHaveCount(10);
  }
}

module.exports = { AdvancedSearchPage };
