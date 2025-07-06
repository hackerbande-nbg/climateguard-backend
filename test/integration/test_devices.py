import json
import pytest
import sys
import random
import string
from pathlib import Path
from test.utils.http_client import HttpClient

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


def generate_unique_device_name(base_name: str) -> str:
    """Generate a unique device name with an 8-character random number"""
    random_suffix = ''.join(random.choices(string.digits, k=8))
    return f"{base_name}_{random_suffix}"


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_device_basic(base_url):
    """Test creating a device with basic information"""
    device_data = {
        "name": generate_unique_device_name("Test Device Basic"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "earth",
        "orientation": "north",
        "shading": 0,   # 0 - full sun, 100 - full shade
        "tags": []
    }

    response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == device_data["name"]
    assert data["latitude"] == device_data["latitude"]
    assert data["longitude"] == device_data["longitude"]
    assert "device_id" in data
    assert "created_at" in data

    # Cleanup
    device_id = data["device_id"]
    http_client.delete(f"{base_url}/devices/{device_id}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_device_with_tags(base_url):
    """Test creating a device with tag relationships"""
    device_data = {
        "name": generate_unique_device_name("Test Device With Tags"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "concrete",
        "orientation": "south",
        "shading": 100,
        "tags": ["urban", "sensor"]
    }

    response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == device_data["name"]
    assert len(data["tags"]) == 2

    # Cleanup
    device_id = data["device_id"]
    http_client.delete(f"{base_url}/devices/{device_id}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_device_missing_required_fields(base_url):
    """Test creating a device with missing required fields"""
    device_data = {
        "description": "A test device missing required fields",
        "latitude": 40.7128,
        "longitude": -74.0060
    }

    response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_devices_no_filters(base_url):
    """Test getting all devices without filters"""
    response = http_client.get(f"{base_url}/devices")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_devices_with_pagination(base_url):
    """Test getting devices with pagination"""
    response = http_client.get(f"{base_url}/devices?limit=5&page=1")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) <= 5

    pagination = data["pagination"]
    assert "total_count" in pagination
    assert "page" in pagination
    assert "limit" in pagination
    assert "total_pages" in pagination
    assert "has_next" in pagination
    assert "has_prev" in pagination


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_devices_with_filters(base_url):
    """Test getting devices with enum filters"""
    response = http_client.get(
        f"{base_url}/devices?ground_cover=grass&orientation=north")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_devices_with_sorting(base_url):
    """Test getting devices with sorting"""
    response = http_client.get(
        f"{base_url}/devices?sort_by=name&sort_order=asc")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert "pagination" in data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_device_by_id(base_url):
    """Test getting a specific device by ID"""
    # First create a device
    device_data = {
        "name": generate_unique_device_name("Test Device Get By ID"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 100,
        "tags": []
    }

    create_response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Get the device by ID
    response = http_client.get(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == device_id
    assert data["name"] == device_data["name"]

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_device_not_found(base_url):
    """Test getting a non-existent device"""
    response = http_client.get(f"{base_url}/devices/999999")
    debug_response_if_not_2xx(response)
    assert response.status_code == 404  # Special case for this ID


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_device_out_of_bounds(base_url):
    """Test getting a device with out of bounds ID"""
    # Test negative ID
    response = http_client.get(f"{base_url}/devices/-1")
    debug_response_if_not_2xx(response)
    assert response.status_code == 400

    # Test ID that's too large
    response = http_client.get(f"{base_url}/devices/2147483648")
    debug_response_if_not_2xx(response)
    assert response.status_code == 400


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_device_regular_not_found(base_url):
    """Test getting a regular non-existent device"""
    response = http_client.get(f"{base_url}/devices/999999")
    debug_response_if_not_2xx(response)
    assert response.status_code == 404


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_update_device(base_url):
    """Test updating a device"""
    # First create a device
    dev_name = generate_unique_device_name("Test Device Update")
    device_data = {
        "name": dev_name,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 0,
        "tags": ["test"]
    }

    create_response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Update the device
    update_data = {
        "name": dev_name,
        "latitude": 41.0000,
        "longitude": -75.0000,
        "ground_cover": "concrete",
        "orientation": "south",
        "shading": 50,
        "tags": ["updated", "test"]
    }

    response = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["latitude"] == update_data["latitude"]
    assert data["longitude"] == update_data["longitude"]
    assert data["ground_cover"] == update_data["ground_cover"]
    assert len(data["tags"]) == 2

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_update_device_not_found(base_url):
    """Test updating a non-existent device"""
    update_data = {
        "name": "Non-existent Device",
        "description": "This device does not exist",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": "full_sun",
        "tags": []
    }

    response = http_client.put(f"{base_url}/devices/999999", json=update_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 422


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_update_device_invalid_enum(base_url):
    """Test updating a device with invalid enum values"""
    # First create a device
    device_data = {
        "name": generate_unique_device_name("Test Device Invalid Update"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 0,
        "tags": []
    }

    create_response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Try to update with invalid enum
    update_data = {
        "name": "Updated Device",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "invalid_ground",
        "orientation": "north",
        "shading": "full_sun",
        "tags": []
    }

    response = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 422  # Validation error

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_delete_device(base_url):
    """Test deleting a device"""
    # First create a device
    device_data = {
        "name": generate_unique_device_name("Test Device Delete"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 0,
        "tags": []
    }

    create_response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Delete the device
    response = http_client.delete(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(response)
    assert response.status_code == 200

    # Verify device is deleted
    get_response = http_client.get(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(get_response)
    assert get_response.status_code == 404


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_delete_device_not_found(base_url):
    """Test deleting a non-existent device"""
    response = http_client.delete(f"{base_url}/devices/999999")
    debug_response_if_not_2xx(response)
    assert response.status_code == 404


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_device_duplicate_name(base_url):
    """Test creating a device with duplicate name"""
    unique_name = generate_unique_device_name("Duplicate Device Name")
    device_data = {
        "name": unique_name,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 0,
        "tags": []
    }

    # Create first device
    create_response1 = http_client.post(
        f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response1)
    assert create_response1.status_code == 201
    device_id1 = create_response1.json()["device_id"]

    # Try to create second device with same name
    create_response2 = http_client.post(
        f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response2)
    assert create_response2.status_code == 409  # Conflict

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id1}")


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_device_tag_relationships_crud(base_url):
    """Test complete CRUD operations maintaining tag relationships"""
    # Create device with tags
    dev_name = generate_unique_device_name("Test Device Tag CRUD")
    device_data = {
        "name": dev_name,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 0,
        "tags": ["urban", "sensor"]
    }

    create_response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]
    assert len(created_device["tags"]) == 2

    # Read device and verify tags
    get_response = http_client.get(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(get_response)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data["tags"]) == 2

    # Update device with different tags
    update_data = {
        "name": dev_name,
        "latitude": 41.0000,
        "longitude": -75.0000,
        "ground_cover": "concrete",
        "orientation": "south",
        "shading": 0,
        "tags": ["outdoor", "active", "scheduled"]
    }

    update_response = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data)
    debug_response_if_not_2xx(update_response)
    assert update_response.status_code == 200
    updated_device = update_response.json()
    assert len(updated_device["tags"]) == 3

    # Delete device (should also remove tag relationships)
    delete_response = http_client.delete(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(delete_response)
    assert delete_response.status_code == 200

    # Verify device is deleted
    get_response2 = http_client.get(f"{base_url}/devices/{device_id}")
    debug_response_if_not_2xx(get_response2)
    assert get_response2.status_code == 404
