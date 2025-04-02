# Bluefin API Tests

## Overview
These tests interact with the REAL Bluefin API to validate the functionality of our Bluefin integration.

## Prerequisites
To run these tests, you must set up the following environment variables:

- `BLUEFIN_NETWORK`: The Bluefin network (e.g., `SUI_STAGING`)
- `BLUEFIN_PRIVATE_KEY`: Your private key for API authentication
- `BLUEFIN_EXCHANGE`: The exchange to use (e.g., `BLUEFIN`)

### Environment Variable Setup
You can set these variables in a `.env` file or export them in your shell:

```bash
export BLUEFIN_NETWORK=SUI_STAGING
export BLUEFIN_PRIVATE_KEY=your_private_key_here
export BLUEFIN_EXCHANGE=BLUEFIN
```

## Running Tests
To run the tests, ensure you have the required dependencies installed:

```bash
pip install pytest pytest-asyncio python-dotenv
```

Then run the tests using pytest:

```bash
pytest test_bluefin_account.py
```

## Important Notes
- These tests make REAL API calls to the Bluefin service
- Ensure you have the necessary credentials and network access
- Be mindful of API rate limits and potential costs
- Sensitive information should NEVER be committed to version control

## Test Coverage
The tests cover:
- Successful account balance retrieval
- Error handling scenarios
- Network resilience checks