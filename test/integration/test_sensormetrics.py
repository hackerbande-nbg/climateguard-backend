import json
import pytest
from test.utils.http_client import HttpClient  # Updated import path

# Load the URL from config/test_config.json
with open("config/test_config.json") as config_file:
    config = json.load(config_file)
    BASE_URL = config["base_url_stage"]

# Initialize the HTTP client with retry logic
http_client = HttpClient(retries=3, retry_on_status=[503])


@pytest.fixture
def sensormetric_payload():
    return {
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184800,
        "temperature": 22.5,
        "humidity": 45.0,
    }


def test_post_sensormetric(sensormetric_payload):
    # Post the sensormetric
    response = http_client.post(
        f"{BASE_URL}/sensormetrics",
        json=sensormetric_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["temperature"] == sensormetric_payload["temperature"]
    assert response_data["humidity"] == sensormetric_payload["humidity"]

    # Get the sensormetric and check it is set
    get_response = http_client.get(f"{BASE_URL}/sensormetrics")
    assert get_response.status_code == 200
    get_response_data = get_response.json()


def test_get_sensormetrics():
    response = http_client.get(f"{BASE_URL}/sensormetrics")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_ping():
    response = http_client.get(f"{BASE_URL}/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


def test_post_sensormetric_with_wrong_device_id(sensormetric_payload):
    # Add invalid temperature to payload
    sensormetric_payload.update({"temperature": "a"})
    # Post the sensormetric
    response = http_client.post(
        f"{BASE_URL}/sensormetrics",
        json=sensormetric_payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422  # Unprocessable Entity
