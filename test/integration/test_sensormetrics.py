import json
import pytest
from test.utils.http_client import HttpClient  # Updated import path

# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URLS = config["base_urls_v1"]
    BASE_URLS_V2 = config["base_urls_v2"]

# Initialize the HTTP client with retry logic and exponential backoff
http_client = HttpClient(retries=3, retry_on_status=[500, 503])


@pytest.fixture
def sensormetric_payload():
    return {
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184800,
        "temperature": 22.5,
        "humidity": 45.0,
    }


@pytest.mark.parametrize("base_url", BASE_URLS)
def test_post_sensormetric(sensormetric_payload, base_url):
    # Post the sensormetric
    response = http_client.post(
        f"{base_url}/sensormetrics",
        json=sensormetric_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["temperature"] == sensormetric_payload["temperature"]
    assert response_data["humidity"] == sensormetric_payload["humidity"]

    # Get the sensormetric and check it is set
    get_response = http_client.get(f"{base_url}/sensormetrics")
    assert get_response.status_code == 200
    get_response_data = get_response.json()


@pytest.mark.parametrize("base_url", BASE_URLS)
def test_get_sensormetrics(base_url):
    response = http_client.get(f"{base_url}/sensormetrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("base_url", BASE_URLS)
def test_ping(base_url):
    response = http_client.get(f"{base_url}/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


@pytest.mark.parametrize("base_url", BASE_URLS)
def test_post_sensormetric_with_wrong_device_id(sensormetric_payload, base_url):
    # Add invalid temperature to payload
    sensormetric_payload.update({"temperature": "a"})
    # Post the sensormetric
    response = http_client.post(
        f"{base_url}/sensormetrics",
        json=sensormetric_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_no_filters(base_url):
    """Test /metrics endpoint without any filters"""
    response = http_client.get(f"{base_url}/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_limit(base_url):
    """Test /metrics endpoint with limit parameter"""
    response = http_client.get(f"{base_url}/metrics?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_unix_timestamps(base_url):
    """Test /metrics endpoint with Unix timestamp filters"""
    min_date = "1617184800"  # 2021-03-31
    max_date = "1617271200"  # 2021-04-01
    response = http_client.get(
        f"{base_url}/metrics?min_date={min_date}&max_date={max_date}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_with_iso_dates(base_url):
    """Test /metrics endpoint with ISO date filters"""
    min_date = "2021-03-31T00:00:00Z"
    max_date = "2021-04-01T00:00:00Z"
    response = http_client.get(
        f"{base_url}/metrics?min_date={min_date}&max_date={max_date}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_invalid_date_format(base_url):
    """Test /metrics endpoint with invalid date format"""
    response = http_client.get(f"{base_url}/metrics?min_date=invalid-date")
    assert response.status_code == 400
