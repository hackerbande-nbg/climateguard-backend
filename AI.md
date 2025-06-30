# AI Planning Document

## New /metrics Endpoint Implementation Plan

### Overview
Create a new `/metrics` endpoint that provides the same data as `/sensormetrics` but with date filtering capabilities using min and max date parameters.

### Strategy

#### 1. API Design
- **Endpoint**: `GET /metrics`
- **Query Parameters**:
  - `min_date` (optional): Unix timestamp or ISO date string for minimum date filter
  - `max_date` (optional): Unix timestamp or ISO date string for maximum date filter
  - `limit` (optional): Number of records to return (default: 100, unlim possible with limit 0)
  - do pagination after 200 entries
- **Response**: Same format as `/sensormetrics` but filtered by date range

#### 2. Implementation Approach

##### Option B: Create separate /metrics endpoint
- New endpoint with dedicated filtering logic
- Keep /sensormetrics unchanged for backward compatibility
- Pros: Clean separation, no breaking changes
- Cons: Code duplication

#### 3. Database Query Strategy
```sql
SELECT * FROM sensormetrics 
WHERE timestamp_server >= min_date 
  AND timestamp_server <= max_date 
ORDER BY timestamp_server DESC 

```

#### 4. Implementation Steps

1. **Create new route in router**
   - Add `/metrics` endpoint to  `v2/routers/metrics.py`
   - Accept query parameters: `min_date`, `max_date`, `limit`

2. **Add query parameter validation**
   - Validate date formats (Unix timestamp or ISO string)
   - Handle timezone considerations

3. **Implement database filtering**
   - Extend SQLModel query with WHERE clauses
   - Use `timestamp_server` field for filtering
   - Maintain ordering by timestamp DESC

4. **Add comprehensive tests**
   - Test date filtering with various formats
   - Test edge cases (invalid dates, large ranges)
   - Test performance with large datasets

#### 5. Date Format Handling
- **Input formats supported**:
  - Unix timestamp: `1617184800`
  - ISO string: `2021-03-31T10:00:00Z`
- **Conversion strategy**: Convert all inputs to Unix timestamps for database queries

#### 6. Error Handling
- Invalid date formats → 400 Bad Request
- Date range too large → 400 Bad Request  
- Missing or malformed parameters → Use defaults

#### 7. Performance Considerations
- Add database index on `timestamp_server` if not exists
- Implement query result caching for common date ranges
- Set reasonable default limits to prevent performance issues

#### 8. Testing Strategy
- Unit tests for date parsing and validation
- Integration tests for v2 endpoints
- Performance tests with large datasets
- Edge case testing (boundary dates, invalid inputs)

### Example Usage
```bash
# Get all metrics from last 24 hours
GET /metrics?min_date=1617184800&max_date=1617271200

# Get last 50 metrics from specific date range
GET /metrics?min_date=2021-03-31T00:00:00Z&max_date=2021-04-01T00:00:00Z&limit=50
```

### Next Steps
1. Implement the endpoint in both v1 and v2 routers
2. Add comprehensive test coverage
3. Update API documentation
4. Consider adding to prod no-write tests
