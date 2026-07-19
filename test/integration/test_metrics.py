import json
import pytest
from uuid import uuid4
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


def create_metric_filter_fixture(base_url):
    """Create isolated devices and metrics through the public API."""
    suffix = uuid4().hex
    tag_name = f"metrics-filter-{suffix}"
    devices = []

    for index in range(3):
        response = http_client.post(
            f"{base_url}/devices",
            json={
                "name": f"metrics-filter-device-{index}-{suffix}",
                "latitude": 49.0,
                "longitude": 8.0,
                "tags": [tag_name] if index < 2 else []
            },
            headers=get_auth_headers_for_test()
        )
        debug_response_if_not_2xx(response)
        assert response.status_code == 201
        devices.append(response.json())

    for device, metric_count in zip(devices, (2, 1, 1)):
        for metric_index in range(metric_count):
            response = http_client.post(
                f"{base_url}/metrics",
                json={
                    "device_name": device["name"],
                    "timestamp_server": 2000000000 + metric_index,
                    "temperature": 20.0 + metric_index
                },
                headers=get_auth_headers_for_test()
            )
            debug_response_if_not_2xx(response)
            assert response.status_code == 200

    return devices, tag_name


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_filters_multiple_device_ids_and_scopes_pagination(base_url):
    devices, _ = create_metric_filter_fixture(base_url)
    selected_ids = [devices[0]["device_id"], devices[1]["device_id"]]

    response = http_client.get(
        f"{base_url}/metrics",
        params={
            "device_ids": f"{selected_ids[0]}, {selected_ids[1]},{selected_ids[0]}",
            "limit": 1,
            "page": 1,
        }
    )
    debug_response_if_not_2xx(response)

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total_count"] == 3
    assert payload["pagination"]["total_pages"] == 3
    assert len(payload["data"]) == 1
    assert {metric["device_id"] for metric in payload["data"]} <= set(selected_ids)

    date_response = http_client.get(
        f"{base_url}/metrics",
        params={
            "device_ids": ",".join(str(device_id) for device_id in selected_ids),
            "min_date": 2000000001,
        }
    )
    assert date_response.status_code == 200
    date_payload = date_response.json()
    assert date_payload["pagination"]["total_count"] == 1
    assert {metric["device_id"] for metric in date_payload["data"]} == {
        selected_ids[0]}


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_filters_by_complete_device_tag(base_url):
    devices, tag_name = create_metric_filter_fixture(base_url)
    tagged_ids = {devices[0]["device_id"], devices[1]["device_id"]}

    response = http_client.get(
        f"{base_url}/metrics",
        params={"tag_category": "device", "tag_name": tag_name}
    )
    debug_response_if_not_2xx(response)

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total_count"] == 3
    assert {metric["device_id"] for metric in payload["data"]} == tagged_ids


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
@pytest.mark.parametrize("params", [
    {"tag_category": "device"},
    {"tag_name": "outdoor"},
    {"device_ids": "1", "tag_category": "device", "tag_name": "outdoor"},
])
def test_get_metrics_rejects_incomplete_or_mixed_device_filters(base_url, params):
    response = http_client.get(f"{base_url}/metrics", params=params)

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
@pytest.mark.parametrize("params", [
    {"device_ids": "999999,999998"},
    {"tag_category": "device", "tag_name": "tag-that-does-not-exist"},
])
def test_get_metrics_returns_empty_pagination_for_unmatched_filter(base_url, params):
    response = http_client.get(f"{base_url}/metrics", params=params)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"] == []
    assert payload["pagination"]["total_count"] == 0
    assert payload["pagination"]["total_pages"] == 1
    assert payload["pagination"]["has_next"] is False


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
@pytest.mark.parametrize("device_ids", [
    "",
    "1,",
    ",1",
    "1,,2",
    "one,2",
    "²,2",
    "0,2",
    "-1,2",
    "1000001",
    "999999999999999999999999999999999999999999999999999999999999",
])
def test_get_metrics_rejects_invalid_device_ids(base_url, device_ids):
    response = http_client.get(
        f"{base_url}/metrics", params={"device_ids": device_ids})

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "device_ids must be a comma-separated list of integers "
        "between 1 and 1000000")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_metrics_openapi_exposes_only_comma_separated_device_ids(base_url):
    response = http_client.get(f"{base_url}/openapi.json")
    debug_response_if_not_2xx(response)

    assert response.status_code == 200
    parameters = response.json()["paths"]["/metrics"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}
    assert "device_ids" in parameter_names
    assert "device_id" not in parameter_names


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
def test_create_metric_with_auth(base_url, ensure_test_device):
    """Test creating a metric with authentication"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "air_pressure": 1013.25,  # Standard atmospheric pressure
        "battery_voltage": 3.7,  # Typical Li-ion battery voltage
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184805
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    # With fixture ensuring device exists, we should get 201 (or 200 depending on API)
    assert response.status_code in [
        200, 201], f"Expected successful creation, got {response.status_code}"


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_unauthorized(base_url, ensure_test_device):
    """Test creating a metric without authentication should fail"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0
    }

    response = http_client.post(f"{base_url}/metrics", json=metric_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 401  # Unauthorized
