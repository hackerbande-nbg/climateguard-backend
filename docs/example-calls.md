# API Example Calls

This document contains example curl commands for all v2 endpoints.

# v2

## Base URL
```
http://localhost:8001/v2
```

## Health Check

### GET /ping
Check if the service is running.

```bash
curl -X GET "http://localhost:8001/v2/ping"
```

**Response:**
```json
{"ping": "pong!"}
```

## Sensor Metrics

### GET /sensormetrics
Retrieve the latest 100 sensor metrics.

```bash
curl -X GET "http://localhost:8001/v2/sensormetrics"
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": "sensor_001",
    "timestamp_device": 1617184800,
    "timestamp_server": 1617184805,
    "temperature": 22.5,
    "humidity": 45.0
  }
]
```

### POST /sensormetrics
Add a new sensor metric.

```bash
curl -X POST "http://localhost:8001/v2/sensormetrics" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor_001",
    "timestamp_device": 1617184800,
    "timestamp_server": 1617184805,
    "temperature": 22.5,
    "humidity": 45.0
  }'
```

**Response:**
```json
{
  "id": 123,
  "device_id": "sensor_001",
  "timestamp_device": 1617184800,
  "timestamp_server": 1617184805,
  "temperature": 22.5,
  "humidity": 45.0
}
```

## Metrics with Filtering

### GET /metrics
Retrieve sensor metrics with optional date filtering and pagination.

#### Basic usage (no filters)
```bash
curl -X GET "http://localhost:8001/v2/metrics"
```

#### With limit
```bash
curl -X GET "http://localhost:8001/v2/metrics?limit=50"
```

#### With Unix timestamp filters
```bash
curl -X GET "http://localhost:8001/v2/metrics?min_date=1617184800&max_date=1617271200"
```

#### With ISO date filters
```bash
curl -X GET "http://localhost:8001/v2/metrics?min_date=2021-03-31T00:00:00Z&max_date=2021-04-01T00:00:00Z"
```

#### With pagination (when >200 total entries)
```bash
curl -X GET "http://localhost:8001/v2/metrics?page=1&limit=50"
```

#### Second page
```bash
curl -X GET "http://localhost:8001/v2/metrics?page=2&limit=50"
```

#### Combined filters with pagination
```bash
curl -X GET "http://localhost:8001/v2/metrics?min_date=1617184800&max_date=1617271200&limit=25&page=1"
```

**Query Parameters:**
- `min_date` (optional): Minimum date filter (Unix timestamp or ISO string)
- `max_date` (optional): Maximum date filter (Unix timestamp or ISO string)
- `limit` (optional): Number of records to return (default: 100, max: 1000)
- `page` (optional): Page number for pagination (default: 1, starts from 1)

**Response (when >200 total entries):**
```json
{
  "data": [
    {
      "id": 1,
      "device_id": "sensor_001",
      "timestamp_device": 1617184800,
      "timestamp_server": 1617184805,
      "temperature": 22.5,
      "humidity": 45.0
    }
  ],
  "pagination": {
    "total_count": 250,
    "page": 1,
    "limit": 50,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

**Response (when ≤200 total entries):**
```json
[
  {
    "id": 1,
    "device_id": "sensor_001",
    "timestamp_device": 1617184800,
    "timestamp_server": 1617184805,
    "temperature": 22.5,
    "humidity": 45.0
  }
]
```

## Error Examples

### Invalid date format
```bash
curl -X GET "http://localhost:8001/v2/metrics?min_date=invalid-date"
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid date format: invalid-date"
}
```

### Invalid temperature in POST
```bash
curl -X POST "http://localhost:8001/v2/sensormetrics" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor_001",
    "timestamp_device": 1617184800,
    "timestamp_server": 1617184805,
    "temperature": "invalid",
    "humidity": 45.0
  }'
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

### Limit too high
```bash
curl -X GET "http://localhost:8001/v2/metrics?limit=2000"
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.number.not_le"
    }
  ]
}
```
