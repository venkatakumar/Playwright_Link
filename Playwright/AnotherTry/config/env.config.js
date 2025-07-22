// Environment configuration
module.exports = {
    // API configuration
    api: {
        baseUrl: 'https://reqres.in/api',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': 'reqres-free-v1'
        }
    },
    // Test data
    testData: {
        loginCredentials: {
            email: 'eve.holt@reqres.in',
            password: 'cityslicka'
        }
    }
};
