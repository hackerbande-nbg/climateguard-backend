# Database Schema Changes - SensorMetric Foreign Key

## Changes Made
- Changed `SensorMetric.device_id` from `Optional[str]` to `Optional[int]` with foreign key constraint to `Device.device_id`
- Added bidirectional relationship with `back_populates`
- Added `Relationship` import from `sqlmodel`
- Added `List` import from `typing`

## Implications and Required Changes

### 1. Database Migration
- **CRITICAL**: Enhanced migration that handles data conversion:
  - Finds all unique device_id values from sensormetric that don't exist as device.name
  - Creates new Device entries using the device_id string as the device name
  - Updates sensormetric.device_id to reference the actual device.device_id (integer)
  - Adds foreign key constraint after data migration
  - **Downgrade**: Reverts device_id back to device names and drops foreign key

### 2. Data Validation
- **RESOLVED**: Migration automatically creates missing Device entries
- All existing `device_id` values will have corresponding `device` table entries after migration
- Auto-created devices will have minimal information (only name field populated)

### 3. API Changes
- Update API endpoints that accept `device_id` in SensorMetric creation/updates
- Change validation to expect integers instead of strings
- Update API documentation/OpenAPI specs
- Consider if you want to expose the relationship in API responses (nested data)

### 4. Application Logic
- Review all code that creates SensorMetric instances
- Update any hardcoded device_id strings to use integer references
- Modify device lookup logic if needed
- **NEW**: Can now use `device.sensor_metrics` to get all metrics for a device
- **NEW**: Can use `sensor_metric.device` to get the associated device
- **IMPORTANT**: Review auto-migrated devices and update their information as needed

### 5. Testing
- Update unit tests for SensorMetric model
- Update integration tests that create sensor metrics
- Test foreign key constraint behavior (cascading deletes, etc.)
- **NEW**: Test relationship loading and lazy loading behavior
- **NEW**: Test migration with various data scenarios

### 6. Frontend/Client Changes
- Update any frontend code that sends device_id as string
- Modify forms/inputs to handle integer device IDs
- Update client-side validation

### 7. Error Handling
- Add proper error handling for foreign key constraint violations
- Handle cases where referenced device doesn't exist

### 8. Performance Considerations
- Foreign key adds referential integrity but may impact insert performance
- Consider indexing strategy for device_id lookups
- Monitor query performance after changes
- **NEW**: Be aware of N+1 queries when accessing relationships - use eager loading when needed

### 9. Documentation
- Update database schema documentation
- Update API documentation
- Update developer guides mentioning the relationship
- **NEW**: Document the new relationship access patterns
- **NEW**: Document the migration process and auto-created device handling

### 10. Post-Migration Tasks
- **NEW**: Review auto-migrated devices and update their metadata
- **NEW**: Consider merging duplicate devices if string identifiers were inconsistent
- **NEW**: Update any external references to use the new integer device IDs
- **NEW**: Update any external references to use the new integer device IDs
