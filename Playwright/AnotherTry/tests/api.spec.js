const { test, expect } = require('@playwright/test');
const config = require('../config/env.config');
const { validateIds, validateEmail, validateNonEmptyString } = require('../utils/validation');

test.describe('API Tests', () => {
    test('POST /login - successful login', async ({ request }) => {
        const response = await request.post(`${config.api.baseUrl}/login`, {
            data: config.testData.loginCredentials,
            headers: config.api.headers
        });

        expect(response.ok()).toBeTruthy();
        const responseBody = await response.json();
        expect(responseBody.token).toBeDefined();
    });

    test('GET /users - validate user data', async ({ request }) => {
        const response = await request.get(`${config.api.baseUrl}/users`, {
            params: {
                page: 2
            },
            headers: {
                'x-api-key': config.api.headers['x-api-key']
            }
        });

        expect(response.ok()).toBeTruthy();
        const responseBody = await response.json();
        const users = responseBody.data;

        // Get all user IDs
        const userIds = users.map(user => user.id);
        await validateIds(userIds);

        // Validate each user's data
        for (const user of users) {
            validateEmail(user.email, '@reqres.in');
            validateNonEmptyString(user.first_name, 'first_name');
            validateNonEmptyString(user.last_name, 'last_name');
        }
    });

    test('POST /login - 400 Bad Request with invalid credentials', async ({ request }) => {
        const response = await request.post(`${config.api.baseUrl}/login`, {
            data: {
                email: "invalid@email.com",
                password: "wrongpassword"
            },
            headers: config.api.headers
        });

        expect(response.status()).toBe(400);
        const responseBody = await response.json();
        expect(responseBody).toHaveProperty('error', 'user not found');
    });

    test('GET /unknown/100 - 404 Not Found for non-existent resource', async ({ request }) => {
        const response = await request.get(`${config.api.baseUrl}/unknown/100`, {
            headers: {
                'x-api-key': config.api.headers['x-api-key']
            }
        });

        expect(response.status()).toBe(404);
        const responseBody = await response.json();
        expect(responseBody).toEqual({});  // ReqRes returns empty object for 404
    });
});