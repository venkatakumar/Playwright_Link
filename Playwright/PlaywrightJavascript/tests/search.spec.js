// tests/search.spec.js
const { test, expect } = require('@playwright/test');
const { SimpleSearchPage } = require('../pages/simpleSearch.page');
const { AdvancedSearchPage } = require('../pages/advancedSearch.page');

test.describe('Planning Register Search', () => {
  test('Simple Search returns results', async ({ page }) => {
    const simpleSearch = new SimpleSearchPage(page);
    await simpleSearch.goto();
    await simpleSearch.search('Belfast');
    await simpleSearch.expectResults();
  });

  test.only('Advanced Search by reference returns results', async ({ page }) => {
    const advancedSearch = new AdvancedSearchPage(page);
    await advancedSearch.goto();
    await advancedSearch.searchByReference('LA04'); // Use a valid reference for real test
    // Optionally, check for no results or error message if reference is not found
    // await advancedSearch.expectNoResults();
    await advancedSearch.expectResults();
  });
});
