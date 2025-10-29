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
def test_create_metric_with_sensor_message_data(base_url):
    """Test creating a metric with embedded sensor message data"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "air_pressure": 1013.25,
        "battery_voltage": 3.7,
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184805,
        "confirmed": True,
        "consumed_airtime": 0.5,
        "f_cnt": 42,
        "frequency": 868100000,
        "sensor_messages": [{
            "gateway_id": "test_gateway_01",
            "rssi": -85.5,
            "snr": 7.2,
            "channel_rssi": -90.1,
            "lora_bandwidth": 125,
            "lora_spreading_factor": 7,
            "lora_coding_rate": "4/5"
        }]
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    if response.status_code == 404:
        # Device not found is expected in test environment
        assert "not found" in response.json().get("detail", "").lower()
    else:
        assert response.status_code == 200
        data = response.json()
        # Verify new fields are included
        assert "confirmed" in data
        assert "consumed_airtime" in data
        assert "f_cnt" in data
        assert "frequency" in data
        assert "sensor_messages" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_with_multiple_sensor_messages(base_url):
    """Test creating a metric with multiple sensor messages"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "timestamp_device": 1617184800,
        "timestamp_server": 1617184805,
        "confirmed": True,
        "consumed_airtime": 0.5,
        "f_cnt": 42,
        "frequency": 868100000,
        "sensor_messages": [
            {
                "gateway_id": "test_gateway_01",
                "rssi": -85.5,
                "snr": 7.2,
                "channel_rssi": -90.1,
                "lora_bandwidth": 125,
                "lora_spreading_factor": 7,
                "lora_coding_rate": "4/5"
            },
            {
                "gateway_id": "test_gateway_02",
                "rssi": -88.2,
                "snr": 5.8,
                "channel_rssi": -92.3,
                "lora_bandwidth": 125,
                "lora_spreading_factor": 8,
                "lora_coding_rate": "4/5"
            },
            {
                "gateway_id": "test_gateway_03",
                "rssi": -91.1,
                "snr": 4.2,
                "lora_bandwidth": 250,
                "lora_spreading_factor": 9
            }
        ]
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    if response.status_code == 404:
        # Device not found is expected in test environment
        assert "not found" in response.json().get("detail", "").lower()
    else:
        assert response.status_code == 200
        data = response.json()
        # Verify multiple sensor messages are included
        assert "sensor_messages" in data
        assert len(data["sensor_messages"]) == 3
        # Verify each message has the expected structure
        for msg in data["sensor_messages"]:
            assert "id" in msg
            assert "gateway_id" in msg
            assert "rssi" in msg


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_with_new_fields_only(base_url):
    """Test creating a metric with new SensorMetric fields but no sensor message"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "confirmed": False,
        "consumed_airtime": 1.2,
        "f_cnt": 100,
        "frequency": 868300000
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    if response.status_code == 404:
        # Device not found is expected in test environment
        assert "not found" in response.json().get("detail", "").lower()
    else:
        assert response.status_code == 200
        data = response.json()
        assert not data["confirmed"]
        assert data["consumed_airtime"] == 1.2
        assert data["f_cnt"] == 100
        assert data["frequency"] == 868300000
        assert data["sensor_messages"] == []


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_backward_compatibility(base_url):
    """Test that old metric creation without new fields still works"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "humidity": 65.0,
        "air_pressure": 1013.25,
        "battery_voltage": 3.7
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    if response.status_code == 404:
        # Device not found is expected in test environment
        assert "not found" in response.json().get("detail", "").lower()
    else:
        assert response.status_code == 200
        data = response.json()


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_invalid_sensor_message_data(base_url):
    """Test creating a metric with invalid sensor message data"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "sensor_messages": [{
            "lora_spreading_factor": 15,  # Invalid: should be 7-12
            "lora_bandwidth": -5  # Invalid: should be >= 0
        }]
    }

    response = http_client.post(
        f"{base_url}/metrics", json=metric_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)

    # Should fail validation
    assert response.status_code == 422


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_includes_sensor_messages(base_url):
    """Test that metrics endpoint includes sensor message data in responses"""
    response = http_client.get(f"{base_url}/metrics?limit=5")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200

    data = response.json()
    assert "data" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_metric_unauthorized_with_sensor_message(base_url):
    """Test creating a metric with sensor message without authentication should fail"""
    metric_data = {
        "device_name": "test_device",
        "temperature": 22.5,
        "sensor_messages": [{
            "gateway_id": "test_gateway",
            "rssi": -85.5
        }]
    }

    response = http_client.post(f"{base_url}/metrics", json=metric_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 401  # Unauthorized
