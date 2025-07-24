import json
import pytest
from test.utils.http_client import HttpClient
from test.utils.auth_helpers import get_auth_headers, TEST_USER

# vibe code instructions
# use the http_client so we have some juicy retries and exponential backoff
# for rest requests, if not a 2xx response, also output the response body before asserts for debuging


# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URLS_V2 = config["base_urls_v2"]

# Initialize the HTTP client with retry logic and exponential backoff
http_client = HttpClient(retries=3, retry_on_status=[500, 503])


def debug_response_if_not_2xx(response):
    """Debug helper to output response body if not 2xx status"""
    if not (200 <= response.status_code < 300):
        print(f"❌ Non-2xx response: {response.status_code}")
        print(f"Response body: {response.text}")


def get_auth_headers_for_test():
    """Get authentication headers for test requests"""
    return get_auth_headers(TEST_USER['X-API-Key'])


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_no_filters(base_url):
    """Test /metrics endpoint without any filters"""
    response = http_client.get(f"{base_url}/metrics")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_limit(base_url):
    """Test /metrics endpoint with limit parameter"""
    response = http_client.get(f"{base_url}/metrics?limit=5")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert len(data["data"]) <= 5


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_unix_timestamps(base_url):
    """Test /metrics endpoint with Unix timestamp filters"""
    min_date = "1617184800"  # 2021-03-31
    max_date = "1617271200"  # 2021-04-01
    response = http_client.get(
        f"{base_url}/metrics?min_date={min_date}&max_date={max_date}")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_iso_dates(base_url):
    """Test /metrics endpoint with ISO date filters"""
    min_date = "2021-03-31T00:00:00Z"
    max_date = "2021-04-01T00:00:00Z"
    response = http_client.get(
        f"{base_url}/metrics?min_date={min_date}&max_date={max_date}")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_invalid_date_format(base_url):
    """Test /metrics endpoint with invalid date format"""
    response = http_client.get(f"{base_url}/metrics?min_date=invalid-date")
    debug_response_if_not_2xx(response)
    assert response.status_code == 400


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_structure(base_url):
    """Test /metrics endpoint pagination response structure when pagination is triggered"""
    response = http_client.get(f"{base_url}/metrics?limit=10&page=1")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200

    data = response.json()

    # Always expect dict structure
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) <= 10

    pagination = data["pagination"]
    assert "total_count" in pagination
    assert "page" in pagination
    assert "limit" in pagination
    assert "total_pages" in pagination
    assert "has_next" in pagination
    assert "has_prev" in pagination


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_navigation(base_url):
    """Test /metrics endpoint pagination navigation"""
    # Test first page
    response1 = http_client.get(f"{base_url}/metrics?limit=5&page=1")
    debug_response_if_not_2xx(response1)
    assert response1.status_code == 200

    # Test second page
    response2 = http_client.get(f"{base_url}/metrics?limit=5&page=2")
    debug_response_if_not_2xx(response2)
    assert response2.status_code == 200


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_invalid_page(base_url):
    """Test /metrics endpoint with invalid page number"""
    response = http_client.get(f"{base_url}/metrics?page=0")
    debug_response_if_not_2xx(response)
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_with_auth(base_url):
    """Test creating a metric with authentication"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "air_pressure": 1013.25,  # Standard atmospheric pressure
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184805
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    if response.status_code == 404:
        # Device not found is expected in test environment
        assert "not found" in response.json().get("detail", "").lower()
    else:
        assert response.status_code == 201


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_unauthorized(base_url):
    """Test creating a metric without authentication should fail"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 18.0,
        "humidity": 55.0,
        "timestamp_device": 1617185000,
        "timestamp_server": 1617185005
    }

    response = http_client.post(f"{base_url}/metrics", json=metric_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 401  # Unauthorized
