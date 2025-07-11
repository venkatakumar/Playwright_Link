// pages/simpleSearch.page.js
const { expect } = require('@playwright/test');

class SimpleSearchPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.searchInput = page.getByRole('textbox', { name: 'Enter your search' })
    this.searchButton = page.getByRole('button', { name: 'Search', exact: true });
    this.results = page.getByTestId('attention-message__title');
  }

  async goto() {
    await this.page.goto('https://planningregister.planningsystemni.gov.uk/simple-search');
  }

  async search(term) {
    await this.searchInput.click(); // Use a valid search term for real test
    await this.searchInput.fill(term);
    await this.searchButton.click();
  }

  async expectResults() {
    await expect(this.results).toBeVisible();
  }
}

module.exports = { SimpleSearchPage };
