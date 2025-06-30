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


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_structure(base_url):
    """Test /metrics endpoint pagination response structure when pagination is triggered"""
    # First, post enough metrics to trigger pagination (need >200 entries)
    # This test assumes the create_test_metrics.py script has been run to create 150+ entries
    response = http_client.get(f"{base_url}/metrics?limit=10&page=1")
    assert response.status_code == 200

    data = response.json()

    # Check if we got pagination response (when >200 total entries) or simple list
    if isinstance(data, dict) and "pagination" in data:
        # Paginated response
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
        assert pagination["page"] == 1
        assert pagination["limit"] == 10
        assert pagination["has_prev"] == False
    else:
        # Simple list response (<=200 total entries)
        assert isinstance(data, list)


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_navigation(base_url):
    """Test /metrics endpoint pagination navigation"""
    # Test first page
    response1 = http_client.get(f"{base_url}/metrics?limit=5&page=1")
    assert response1.status_code == 200

    # Test second page
    response2 = http_client.get(f"{base_url}/metrics?limit=5&page=2")
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # If we have paginated responses, ensure they're different
    if isinstance(data1, dict) and isinstance(data2, dict):
        if "pagination" in data1 and "pagination" in data2:
            # Ensure different pages return different data
            page1_ids = [item["id"] for item in data1["data"]]
            page2_ids = [item["id"] for item in data2["data"]]
            assert page1_ids != page2_ids  # Different pages should have different data


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_invalid_page(base_url):
    """Test /metrics endpoint with invalid page number"""
    response = http_client.get(f"{base_url}/metrics?page=0")
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("base_url", BASE_URLS_V2)
def test_get_metrics_pagination_high_page_number(base_url):
    """Test /metrics endpoint with very high page number"""
    response = http_client.get(f"{base_url}/metrics?page=9999&limit=10")
    assert response.status_code == 200

    data = response.json()
    if isinstance(data, dict) and "pagination" in data:
        # Should return empty data for page beyond available data
        assert len(data["data"]) == 0
    else:
        # If not paginated, should return empty list
        assert isinstance(data, list)
