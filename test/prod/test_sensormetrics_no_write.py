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
