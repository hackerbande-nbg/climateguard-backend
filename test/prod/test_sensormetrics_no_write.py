import json
import requests
import pytest
import hashlib

# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URL = config["base_url_prod"]


@pytest.fixture
def sensormetric_payload():
    return {
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184800,
        "device_id": "lora_test_1",
        "temperature": 22.5,
        "humidity": 45.0,
    }


def test_get_sensormetrics():
    response = requests.get(f"{BASE_URL}/sensormetrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ping():
    response = requests.get(f"{BASE_URL}/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


def test_post_sensormetric_with_wrong_temperature(sensormetric_payload):
    # add device_id from payload
    sensormetric_payload.update({"temperature": "a"})
    # Post the sensormetric
    response = requests.post(
        f"{BASE_URL}/sensormetrics",
        json=sensormetric_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_get_metrics():
    """Test /metrics endpoint"""
    response = requests.get(f"{BASE_URL}/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_metrics_with_filters():
    """Test /metrics endpoint with date filters"""
    response = requests.get(
        f"{BASE_URL}/metrics?min_date=1617184800&max_date=1617271200&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_metrics_invalid_date():
    """Test /metrics endpoint with invalid date format"""
    response = requests.get(f"{BASE_URL}/metrics?min_date=invalid-date")
    assert response.status_code == 400


def test_get_metrics_pagination():
    """Test /metrics endpoint pagination"""
    response = requests.get(f"{BASE_URL}/metrics?limit=10&page=1")
    assert response.status_code == 200

    data = response.json()
    # Should work regardless of whether pagination is triggered
    if isinstance(data, dict) and "pagination" in data:
        assert "data" in data
        assert isinstance(data["data"], list)
    else:
        assert isinstance(data, list)


def test_get_metrics_pagination_with_filters():
    """Test /metrics endpoint pagination with date filters"""
    response = requests.get(
        f"{BASE_URL}/metrics?min_date=1617184800&max_date=1617271200&limit=5&page=1")
    assert response.status_code == 200

    data = response.json()
    if isinstance(data, dict) and "pagination" in data:
        assert len(data["data"]) <= 5
    else:
        assert isinstance(data, list)
