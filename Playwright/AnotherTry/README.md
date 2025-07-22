# API Automation Framework with Playwright MCP

This project demonstrates API automation testing using Playwright with VS Code's Model Context Protocol (MCP) server.

## Prerequisites

1. Visual Studio Code with the following extensions:
   - GitHub Copilot Chat
   - Playwright Test for VSCode

2. Ensure the Playwright MCP server is running in VS Code:
   - Open VS Code Command Palette (Ctrl/Cmd + Shift + P)
   - Type and select "Copilot: Open Chat View"
   - The MCP server should start automatically

## Project Structure

```
├── config/
│   └── env.config.js         # Environment configuration
├── tests/
│   └── api.spec.js          # API test specifications
├── utils/
│   └── validation.js        # Utility functions for validation
└── playwright.config.js     # Playwright configuration
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

## Running Tests

Before running tests:
1. Make sure VS Code is open
2. Ensure the Copilot Chat view is open (this runs the MCP server)

To run the tests:
```bash
npm test
```

To view the HTML report after test execution:
```bash
npx playwright show-report
```

## API Tests

The framework includes tests for:

1. POST /login
   - Authentication with provided credentials
   - Token validation

2. GET /users
   - Validates user data structure
   - Ensures IDs are unique and in ascending order
   - Validates email format (@reqres.in)
   - Verifies non-empty name fields

## Configuration

- API endpoints and test data are configured in `config/env.config.js`
- Validation utilities are available in `utils/validation.js`
- Playwright configuration in `playwright.config.js`

## Notes

- This project uses VS Code's built-in Playwright MCP server instead of local browser installations
- No need to install browsers locally as tests run through the MCP server
- Make sure the MCP server is running before executing tests
