"""
Authentication helper utilities for integration tests.

This module provides:
- Test user registration and API key management
- Authentication header helpers  
- Authenticated HTTP client setup
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from test.utils.http_client import HttpClient
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

# Test user configuration from environment variables
TEST_USER = {
    'username': os.getenv('TEST_USER_NAME', 'test_user'),
    'email': f"{os.getenv('TEST_USER_NAME', 'test_user')}@example.com",
    'expected_api_key': os.getenv('TEST_USER_PW', 'aslkdhl2389042230asdhl')
}

# Global variable to store the actual API key after registration
_test_api_key: Optional[str] = None


def get_auth_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Get authentication headers for API requests.

    Args:
        api_key: API key to use (defaults to test user's key)

    Returns:
        Dict with authentication headers
    """
    global _test_api_key

    key_to_use = api_key or _test_api_key
    if not key_to_use:
        raise ValueError("No API key available. Register test user first.")

    return {
        "X-API-Key": key_to_use
    }


def get_auth_headers_bearer(api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Get Bearer token authentication headers for API requests.

    Args:
        api_key: API key to use (defaults to test user's key)

    Returns:
        Dict with Bearer authentication headers
    """
    global _test_api_key

    key_to_use = api_key or _test_api_key
    if not key_to_use:
        raise ValueError("No API key available. Register test user first.")

    return {
        "Authorization": f"Bearer {key_to_use}"
    }


def register_test_user(base_url: str, http_client: HttpClient) -> str:
    """
    Register test user and return API key.

    Args:
        base_url: Base URL for API
        http_client: HTTP client instance

    Returns:
        API key for test user

    Raises:
        Exception: If registration fails
    """
    global _test_api_key

    # If already registered, return existing key
    if _test_api_key:
        return _test_api_key

    registration_data = {
        'username': TEST_USER['username'],
        'email': TEST_USER['email']
    }

    print(f"🔐 Registering test user: {TEST_USER['username']}")

    response = http_client.post(
        f"{base_url}/auth/register", json=registration_data)

    if response.status_code == 201:
        data = response.json()
        _test_api_key = data['api_key']
        print(f"✅ Test user registered successfully")
        print(f"   API Key: {_test_api_key}")
        return _test_api_key

    elif response.status_code == 409:
        # User already registered, this is expected in some test scenarios
        print(f"⚠️  Test user already registered - this is expected")
        print(f"   Using pre-configured API key for testing")
        _test_api_key = TEST_USER['expected_api_key']
        return _test_api_key

    else:
        print(f"❌ Test user registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception(
            f"Failed to register test user: {response.status_code}")


def get_authenticated_client(base_url: str) -> HttpClient:
    """
    Get HTTP client with authentication headers pre-configured.

    Args:
        base_url: Base URL for API

    Returns:
        HTTP client with auth headers
    """
    http_client = HttpClient()

    # Register test user if not already done
    if not _test_api_key:
        register_test_user(base_url, http_client)

    # Add default headers to client
    auth_headers = get_auth_headers()
    http_client.default_headers = auth_headers

    return http_client


def reset_test_user():
    """Reset test user state (for test cleanup)"""
    global _test_api_key
    _test_api_key = None


def debug_auth_response(response, operation: str = "API call"):
    """Debug helper for authentication-related responses"""
    if response.status_code == 401:
        print(f"❌ Authentication failed for {operation}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    elif response.status_code == 403:
        print(f"❌ Access forbidden for {operation}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    elif not (200 <= response.status_code < 300):
        print(f"❌ {operation} failed: {response.status_code}")
        print(f"   Response: {response.text}")
