import pytest
import asyncio
import os
from dotenv import load_dotenv

from services.bluefin_service import BluefinService
from bluefin_v2_client import BluefinClient, Networks, Exchanges

# Load environment variables from .env file
load_dotenv()

class TestBluefinAccountBalance:
    """
    Test suite for Bluefin account balance retrieval functionality.
    
    These tests interact with the REAL Bluefin API to verify:
    - Successful account balance retrieval
    - Proper error handling
    - Correct data structure
    """

    @pytest.fixture
    async def bluefin_service(self):
        """
        Fixture to create a BluefinService instance using REAL credentials.
        
        Requires the following environment variables:
        - BLUEFIN_NETWORK: Bluefin network (e.g., SUI_STAGING)
        - BLUEFIN_PRIVATE_KEY: Private key for API authentication
        - BLUEFIN_EXCHANGE: Exchange to use (e.g., BLUEFIN)
        """
        # Validate required environment variables
        required_vars = ['BLUEFIN_NETWORK', 'BLUEFIN_PRIVATE_KEY', 'BLUEFIN_EXCHANGE']
        for var in required_vars:
            if not os.getenv(var):
                pytest.skip(f"Skipping test: {var} environment variable not set")

        # Initialize service with real credentials
        service = BluefinService(
            network=os.getenv('BLUEFIN_NETWORK'), 
            private_key=os.getenv('BLUEFIN_PRIVATE_KEY'), 
            exchange=Exchanges[os.getenv('BLUEFIN_EXCHANGE')]
        )
        
        return service

    @pytest.mark.asyncio
    async def test_get_account_balance_success(self, bluefin_service):
        """
        Test successful account balance retrieval using REAL API.
        
        Verifies that:
        - The method returns a dictionary
        - The balance contains expected keys
        - No exceptions are raised during retrieval
        """
        # Retrieve actual account balance
        balance = await bluefin_service.get_account_balance()

        # Assertions
        assert isinstance(balance, dict), "Balance should be a dictionary"
        assert 'total_balance' in balance, "Balance should contain total_balance"
        assert 'available_balance' in balance, "Balance should contain available_balance"
        assert 'positions' in balance, "Balance should contain positions"
        assert 'currency' in balance, "Balance should contain currency"

    @pytest.mark.asyncio
    async def test_get_account_balance_error_handling(self, bluefin_service):
        """
        Test error handling during account balance retrieval.
        
        Verifies that:
        - Exceptions from the client are properly caught and re-raised
        - A RuntimeError is raised with an appropriate error message
        """
        # Temporarily modify the client to simulate an error scenario
        original_client = bluefin_service.client
        try:
            # Simulate an error by using an invalid configuration
            bluefin_service.client = BluefinClient(
                network=Networks.SUI_STAGING, 
                private_key='invalid_key',
                exchange=Exchanges.BLUEFIN
            )

            # Expect a RuntimeError when trying to retrieve balance
            with pytest.raises(RuntimeError, match="Account balance retrieval error"):
                await bluefin_service.get_account_balance()
        
        finally:
            # Restore the original client
            bluefin_service.client = original_client

    @pytest.mark.asyncio
    async def test_get_account_balance_network_resilience(self, bluefin_service):
        """
        Test resilience against potential network issues.
        
        Verifies:
        - The method handles potential network connectivity problems
        - Appropriate error messages are generated
        """
        try:
            # Attempt to retrieve balance
            balance = await bluefin_service.get_account_balance()
            
            # Basic sanity checks
            assert balance is not None, "Balance should not be None"
            assert isinstance(balance, dict), "Balance should be a dictionary"
        
        except Exception as e:
            # If an exception occurs, ensure it's a known type of error
            assert isinstance(e, (RuntimeError, ConnectionError)), "Unexpected error type"

# Optional: Add configuration for running tests
if __name__ == '__main__':
    pytest.main([__file__])