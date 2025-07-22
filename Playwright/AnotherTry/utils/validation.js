// API request helper functions
const { expect } = require('@playwright/test');

/**
 * Validates array of IDs are unique and in ascending order
 * @param {Array<number>} ids - Array of IDs to validate
 */
async function validateIds(ids) {
    // Check for uniqueness
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length, 'IDs should be unique');

    // Check for ascending order
    const sortedIds = [...ids].sort((a, b) => a - b);
    expect(ids).toEqual(sortedIds, 'IDs should be in ascending order');
}

/**
 * Validates email format
 * @param {string} email - Email to validate
 * @param {string} domain - Domain to check for
 */
function validateEmail(email, domain) {
    expect(email).toContain(domain, `Email should contain ${domain}`);
}

/**
 * Validates string is non-empty
 * @param {string} value - String to validate
 * @param {string} fieldName - Name of the field being validated
 */
function validateNonEmptyString(value, fieldName) {
    expect(typeof value).toBe('string', `${fieldName} should be a string`);
    expect(value.length).toBeGreaterThan(0, `${fieldName} should not be empty`);
}

module.exports = {
    validateIds,
    validateEmail,
    validateNonEmptyString
};
