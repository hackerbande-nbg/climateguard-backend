import json
import pytest
import random
import string
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


def get_auth_headers_for_test():
    """Get authentication headers for test requests"""
    return get_auth_headers(TEST_USER['X-API-Key'])


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
        "comment": "Basic test device",
        "tags": []
    }

    response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == device_data["name"]
    assert data["latitude"] == device_data["latitude"]
    assert data["longitude"] == device_data["longitude"]
    assert data["comment"] == device_data["comment"]
    assert "device_id" in data
    assert "created_at" in data

    # Cleanup
    device_id = data["device_id"]
    http_client.delete(f"{base_url}/devices/{device_id}",
                       headers=get_auth_headers_for_test())


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_create_device_unauthorized(base_url):
    """Test creating a device without authentication should fail"""
    device_data = {
        "name": generate_unique_device_name("Test Device Unauthorized"),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "earth",
        "orientation": "north",
        "shading": 0,
        "tags": []
    }

    response = http_client.post(f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(response)
    assert response.status_code == 401  # Unauthorized


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
        "comment": "Device with tags for testing",
        "tags": ["urban", "sensor"]
    }

    response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == device_data["name"]
    assert data["comment"] == device_data["comment"]
    assert len(data["tags"]) == 2

    # Cleanup
    device_id = data["device_id"]
    http_client.delete(f"{base_url}/devices/{device_id}",
                       headers=get_auth_headers_for_test())


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
    assert response.status_code == 401  # Validation error


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_devices_no_filters(base_url):
    """Test getting all devices without filters"""
    response = http_client.get(
        f"{base_url}/devices", headers=get_auth_headers_for_test())
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
    response = http_client.get(
        f"{base_url}/devices?limit=5&page=1", headers=get_auth_headers_for_test())
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
        f"{base_url}/devices?ground_cover=grass&orientation=north", headers=get_auth_headers_for_test())
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
        f"{base_url}/devices?sort_by=name&sort_order=asc", headers=get_auth_headers_for_test())
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

    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Get the device by ID
    response = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == device_id
    assert data["name"] == device_data["name"]

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}",
                       headers=get_auth_headers_for_test())


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
    assert response.status_code == 422

    # Test ID that's too large
    response = http_client.get(f"{base_url}/devices/2147483648")
    debug_response_if_not_2xx(response)
    assert response.status_code == 422


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

    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
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
        f"{base_url}/devices/{device_id}", json=update_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["latitude"] == update_data["latitude"]
    assert data["longitude"] == update_data["longitude"]
    assert data["ground_cover"] == update_data["ground_cover"]
    assert len(data["tags"]) == 2

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}",
                       headers=get_auth_headers_for_test())


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
    assert response.status_code == 401


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

    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
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
    assert response.status_code == 401  # Validation error

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id}",
                       headers=get_auth_headers_for_test())


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

    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]

    # Delete the device
    response = http_client.delete(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(response)
    assert response.status_code == 200

    # Verify device is deleted
    get_response = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(get_response)
    assert get_response.status_code == 404


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_delete_device_not_found(base_url):
    """Test deleting a non-existent device"""
    response = http_client.delete(f"{base_url}/devices/999999")
    debug_response_if_not_2xx(response)
    assert response.status_code == 401


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
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(create_response1)
    assert create_response1.status_code == 201
    device_id1 = create_response1.json()["device_id"]

    # Try to create second device with same name
    create_response2 = http_client.post(
        f"{base_url}/devices", json=device_data)
    debug_response_if_not_2xx(create_response2)
    assert create_response2.status_code == 401

    # Cleanup
    http_client.delete(f"{base_url}/devices/{device_id1}",
                       headers=get_auth_headers_for_test())


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
        "comment": "Device for CRUD tag testing",
        "tags": ["urban", "sensor"]
    }

    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]
    assert len(created_device["tags"]) == 2
    assert created_device["comment"] == device_data["comment"]

    # Read device and verify tags
    get_response = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(get_response)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data["tags"]) == 2
    assert get_data["comment"] == device_data["comment"]

    # Update device with different tags
    update_data = {
        "name": dev_name,
        "latitude": 41.0000,
        "longitude": -75.0000,
        "ground_cover": "concrete",
        "orientation": "south",
        "shading": 0,
        "comment": "Updated device comment for CRUD testing",
        "tags": ["outdoor", "active", "scheduled"]
    }

    update_response = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(update_response)
    assert update_response.status_code == 200
    updated_device = update_response.json()
    assert len(updated_device["tags"]) == 3
    assert updated_device["comment"] == update_data["comment"]

    # Delete device (should also remove tag relationships)
    delete_response = http_client.delete(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(delete_response)
    assert delete_response.status_code == 200

    # Verify device is deleted
    get_response2 = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(get_response2)
    assert get_response2.status_code == 404


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_device_comment_field_crud(base_url):
    """Test complete CRUD operations specifically for the comment field"""
    # Create device with comment
    dev_name = generate_unique_device_name("Test Device Comment CRUD")
    original_comment = "This is the original comment for testing purposes"
    device_data = {
        "name": dev_name,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ground_cover": "grass",
        "orientation": "north",
        "shading": 25,
        "comment": original_comment,
        "tags": ["comment-test"]
    }

    # Create device
    create_response = http_client.post(
        f"{base_url}/devices", json=device_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(create_response)
    assert create_response.status_code == 201
    created_device = create_response.json()
    device_id = created_device["device_id"]
    assert created_device["comment"] == original_comment

    # Read device and verify comment persisted
    get_response = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(get_response)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["comment"] == original_comment

    # Update device with new comment
    updated_comment = "This is the updated comment after modification"
    update_data = {
        "name": dev_name,
        "comment": updated_comment,
        "shading": 75
    }

    update_response = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(update_response)
    assert update_response.status_code == 200
    updated_device = update_response.json()
    assert updated_device["comment"] == updated_comment
    assert updated_device["shading"] == 75

    # Read device again to verify comment was updated
    get_response2 = http_client.get(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(get_response2)
    assert get_response2.status_code == 200
    get_data2 = get_response2.json()
    assert get_data2["comment"] == updated_comment
    assert get_data2["shading"] == 75

    # Test updating device without comment field (should preserve existing comment)
    update_data_no_comment = {
        "shading": 50
    }

    update_response2 = http_client.put(
        f"{base_url}/devices/{device_id}", json=update_data_no_comment, headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(update_response2)
    assert update_response2.status_code == 200
    updated_device2 = update_response2.json()
    assert updated_device2["comment"] == updated_comment  # Should be preserved
    assert updated_device2["shading"] == 50

    # Cleanup
    delete_response = http_client.delete(
        f"{base_url}/devices/{device_id}", headers=get_auth_headers_for_test())
    debug_response_if_not_2xx(delete_response)
    assert delete_response.status_code == 200
