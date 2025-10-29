# AI Spec

## Current Status

We have added new fields to the SensorMetric model and created a new SensorMessage model with proper relationships. The models are complete with tag associations following the vibe code instructions.

## Implementation Plan for SensorMessage Integration

### New Model Fields Added to SensorMetric:

- `confirmed: Optional[bool] = None`
- `consumed_airtime: Optional[float] = None`
- `f_cnt: Optional[int] = None`
- `frequency: Optional[int] = None`

### New Model: SensorMessage

Complete LoRaWAN message metadata model with relationships to Device, SensorMetric, and Tags.

## Implementation Notes

- Added proper field validation for LoRa parameters (spreading factor 7-12, positive integers for bandwidth and frequency)
- Schema design supports both standalone sensor messages and nested messages within metrics
- Tag support included in all schemas following the established pattern
- **Step 2 Complete**: Metrics router now handles new SensorMetric fields and optional multiple sensor message data with atomic transactions
- Used flush() before commit to ensure proper ID assignment for foreign key relationships
- Added comprehensive error handling and rollback on failure
- Updated response format to use SensorMetricRead schema with nested sensor messages
- **Updated**: Metrics endpoint now supports multiple sensor messages per metric creation request for comprehensive LoRaWAN data ingestion
- **Greenlet Fix**: Resolved async/await issues by constructing SensorMessageRead objects manually instead of using dictionary conversion, preventing lazy loading attempts outside of async context

## Implementation Steps

### Step 1: Update Schemas (schemas.py) ✅ COMPLETED

- [x] Add `SensorMessageCreate` schema for creating sensor messages
- [x] Add `SensorMessageRead` schema for reading sensor messages
- [x] Add `SensorMessageUpdate` schema for updating sensor messages
- [x] Update `CreateMetricRequest` to include the new SensorMetric fields (confirmed, consumed_airtime, f_cnt, frequency)
- [x] Update `CreateMetricRequest` to optionally include sensor message data
- [x] Add nested sensor message support to metric read responses via `SensorMetricRead` schema

### Step 2: Update Metrics Router (v2/routers/metrics.py) ✅ COMPLETED

- [x] Modify `/metrics` POST endpoint to accept optional sensor message data
- [x] When creating a metric, also create associated SensorMessage if data provided
- [x] Update metric responses to include related sensor messages
- [x] Ensure proper transaction handling (both metric and message created or both fail)
- [x] Add the new SensorMetric fields to the create/update operations
- [x] Update GET `/metrics` endpoint to return SensorMetricRead format with sensor messages
- [x] Maintain backward compatibility with existing metric creation workflows

### Step 3: Add Tests (test/integration/test_messages.py) ✅ COMPLETED

- [x] Test creating metrics with embedded sensor message data
- [x] Test creating metrics with new SensorMetric fields but no sensor message
- [x] Test backward compatibility with existing metric creation (without message data)
- [x] Test creating metrics with invalid sensor message data (validation tests)
- [x] Test that metrics endpoint includes sensor message data in responses
- [x] Test authentication requirements for metric creation with sensor messages
- [x] Test error scenarios (invalid data, missing devices, etc.)

### Step 4: Create Messages Router (v2/routers/messages.py) - NOT IMPLEMENTED

- [ ] Create new router for standalone sensor message operations
- [ ] Add GET `/messages` endpoint with filtering and pagination
- [ ] Add POST `/messages` endpoint for creating standalone messages
- [ ] Add GET `/messages/{id}` endpoint for individual message retrieval
- [ ] Follow same authentication patterns as metrics router
- [ ] Include proper error handling and response formatting
- [ ] Add router to v2/api.py

**Decision**: This step was deprioritized as the metrics endpoint now handles sensor message data as nested objects, which covers the primary use case.

### Step 5: Update Database Migration

- [ ] Use `make db-mig-gen MSG="add sensor message model and new metric fields"`
- [ ] Use `make db-migrate-apply` to apply the migration
- [ ] Verify migration includes all new fields and relationships

### Step 6: Integration Testing

- [x] Test full workflow: device -> metric with message data -> retrieval (via test_messages.py)
- [x] Test backward compatibility with existing metric creation (without message data)
- [ ] Verify tag associations work correctly for both metrics and messages (TODO: tags not fully implemented yet)
- [x] Ensure existing tests in test_metrics.py continue to pass unchanged

## Current Implementation Status

### ✅ COMPLETED

1. **Models**: SensorMessage model and new SensorMetric fields added with proper relationships
2. **Schemas**: Complete schema set for SensorMessage and updated CreateMetricRequest
3. **Metrics Router**: Updated to handle new fields and optional sensor message data
4. **Tests**: Comprehensive test suite for metrics with sensor message integration
5. **Transaction Safety**: Atomic operations for creating metrics with sensor messages

### 🔄 IN PROGRESS / TODO

1. **Database Migration**: Need to generate and apply migration for model changes
2. **Tags Integration**: Sensor message tags are defined but not fully loaded in responses
3. **Standalone Messages Router**: Optional - could be added later if needed

### 📋 MISSING IMPORTS FIX NEEDED

The metrics router is missing the `parse_date_parameter` function import/definition that's used in the date filtering logic.
