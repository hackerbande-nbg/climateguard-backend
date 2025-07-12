import json
import pytest
import sys
from pathlib import Path
from test.utils.http_client import HttpClient
from test.utils.auth_helpers import TEST_USER, get_auth_headers, debug_auth_response

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# vibe code instructions
# use the http_client so we have some juicy retries and exponential backoff
# for rest requests, if not a 2xx response, also output the response body before asserts for debuging

# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URLS_V2 = config["base_urls_v2"]

# Initialize the HTTP client with retry logic and exponential backoff
http_client = HttpClient()


def debug_response_if_not_2xx(response):
    """Debug helper to output response body if not 2xx status"""
    if not (200 <= response.status_code < 300):
        print(f"❌ Non-2xx response: {response.status_code}")
        print(f"Response body: {response.text}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_register_nonexistent_user(base_url):
    """Test registration with non-existent username should fail"""
    registration_data = {
        "username": "nonexistent_user_12345",
        "email": "nonexistent@example.com"
    }

    response = http_client.post(
        f"{base_url}/auth/register", json=registration_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_register_already_registered_user(base_url):
    """Test registration with already registered user should fail"""
    registration_data = {
        "username": TEST_USER['username'],
        "email": TEST_USER['email']
    }

    response = http_client.post(
        f"{base_url}/auth/register", json=registration_data)
    debug_response_if_not_2xx(response)

    # Should be 409 if user already registered, or 201 if this is first registration
    assert response.status_code in [201, 409]

    if response.status_code == 409:
        data = response.json()
        assert "already registered" in data["detail"].lower()


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_user_info_invalid_auth(base_url):
    """Test getting user info with invalid authentication"""
    headers = get_auth_headers("invalid_api_key_12345678901234567890")

    response = http_client.get(f"{base_url}/auth/users/me", headers=headers)
    debug_auth_response(response, "get user info with invalid auth")
    assert response.status_code == 401


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_user_info_no_auth(base_url):
    """Test getting user info without authentication"""
    response = http_client.get(f"{base_url}/auth/users/me")
    debug_auth_response(response, "get user info without auth")
    assert response.status_code == 401


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_regenerate_api_key(base_url):
    """Test API key regeneration"""
    headers = get_auth_headers(TEST_USER['expected_api_key'])

    response = http_client.post(
        f"{base_url}/auth/regenerate-key", headers=headers)
    debug_auth_response(response, "regenerate API key")

    data = response.json()
    assert "api_key" in data
    assert len(data["api_key"]) == 32
    assert data["username"] == TEST_USER['username']


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_regenerate_api_key_unauthorized(base_url):
    """Test API key regeneration without authentication"""
    response = http_client.post(f"{base_url}/auth/regenerate-key")
    debug_auth_response(response, "regenerate API key without auth")
    assert response.status_code == 401
