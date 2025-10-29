import json
import pytest
from test.utils.http_client import HttpClient
from test.utils.auth_helpers import get_auth_headers, TEST_USER

# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URLS_V2 = config["base_urls_v2"]

# Initialize the HTTP client with retry logic and exponential backoff
http_client = HttpClient(retries=3, retry_on_status=[500, 503])


def get_auth_headers_for_test():
    """Get authentication headers for test requests"""
    return get_auth_headers(TEST_USER['X-API-Key'])


@pytest.fixture(scope="session", autouse=True)
def ensure_test_device():
    """
    Fixture that ensures test_device exists before any tests run.
    Runs once per test session and is automatically used.
    Handles gracefully if device already exists.
    """
    device_data = {
        "name": "test_device",
        "latitude": 52.52,
        "longitude": 13.405,
        "comment": "Automated test device - created by test fixture"
    }

    # Try to create device on all configured base URLs
    for base_url in BASE_URLS_V2:
        try:
            response = http_client.post(
                f"{base_url}/devices",
                json=device_data,
                headers=get_auth_headers_for_test()
            )

            if response.status_code == 201:
                print(f"✅ Created test_device on {base_url}")
            elif response.status_code == 409 or response.status_code == 400:
                # Device already exists - this is fine
                print(f"ℹ️ test_device already exists on {base_url}")
            else:
                # Log unexpected status but don't fail - tests might still work
                print(
                    f"⚠️ Unexpected status {response.status_code} creating test_device on {base_url}")
                print(f"Response: {response.text}")
        except Exception as e:
            # Log but don't fail - some endpoints might not be available
            print(f"⚠️ Could not ensure test_device on {base_url}: {str(e)}")

    yield  # Tests run here

    # Cleanup after all tests (optional - you might want to keep the device)
    # Uncomment if you want to delete the test device after tests
    # for base_url in BASE_URLS_V2:
    #     try:
    #         http_client.delete(
    #             f"{base_url}/devices/test_device",
    #             headers=get_auth_headers_for_test()
    #         )
    #     except:
    #         pass
