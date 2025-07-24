# Air Pressure Field Implementation Plan

## Overview
The `air_pressure` field already exists in the `SensorMetric` model but needs full implementation across the API endpoints and tests.

## Current State Analysis
- ✅ `SensorMetric.air_pressure: Optional[float]` already exists in models.py
- ✅ **COMPLETED:** Added to `CreateMetricRequest` in metrics.py router
- ✅ **COMPLETED:** Added to test data in test_metrics.py
- ✅ **COMPLETED:** Included in metric creation endpoint

## Implementation Steps

### 1. Update API Models (metrics.py) ✅ COMPLETED
**File:** `/home/andi/git/climateguard-backend/project/app/v2/routers/metrics.py`

- ✅ Add `air_pressure: Optional[float] = None` to `CreateMetricRequest` class
- ✅ Update the `create_metric` endpoint to handle `air_pressure` from request data
- ✅ Add air_pressure to the `SensorMetric` creation in `create_metric` function

### 2. Update Integration Tests (test_metrics.py) ✅ COMPLETED
**File:** `/home/andi/git/climateguard-backend/test/integration/test_metrics.py`

- ✅ Add `air_pressure` field to test metric data in `test_create_metric_with_auth`
- ✅ Add dedicated test case `test_create_metric_with_air_pressure` to verify air pressure handling
- ✅ Update existing test data to include air pressure values for comprehensive testing
- ✅ Add test case for air pressure validation (extreme values testing)
- ✅ Add test case `test_create_metric_without_air_pressure` for backwards compatibility
- ✅ Add test case `test_create_metric_extreme_air_pressure_values` for edge cases

### 3. API Documentation Updates ✅ AUTOMATIC
- ✅ The existing endpoint documentation will automatically include air_pressure once added to `CreateMetricRequest`
- ✅ Ensure OpenAPI schema reflects the new field

### 4. Validation Considerations
- ℹ️ **NOTE:** No strict bounds validation added - accepting all float values for flexibility
- ℹ️ Extreme values (300-1100 hPa range) are tested but not restricted

## Changes Made

### ✅ metrics.py Changes Applied:
1. ✅ Updated `CreateMetricRequest` class with `air_pressure: Optional[float] = None`
2. ✅ Updated `create_metric` function to include `air_pressure=metric_data.air_pressure`

### ✅ test_metrics.py Changes Applied:
1. ✅ Updated `test_create_metric_with_auth` to include air pressure (1013.25 hPa)
2. ✅ Added `test_create_metric_with_air_pressure` dedicated test case
3. ✅ Added `test_create_metric_without_air_pressure` for backwards compatibility
4. ✅ Added `test_create_metric_extreme_air_pressure_values` for edge case testing

## Testing Strategy ✅ IMPLEMENTED
- ✅ Test metric creation with air pressure values
- ✅ Test metric creation without air pressure (optional field)
- ✅ Test retrieval of metrics with air pressure data
- ✅ Test edge cases (very high/low pressure values)
- ✅ Verify backwards compatibility (existing metrics without air pressure)

## Database Considerations
- ✅ No schema changes needed (field already exists)
- ✅ Existing records will have NULL air_pressure values (acceptable)

## Deployment Notes
- ✅ This is a non-breaking change since the field is optional
- ✅ Existing API consumers can continue without changes
- ✅ New consumers can start sending air pressure data immediately after deployment

## Implementation Status: ✅ COMPLETE
All planned changes have been successfully implemented and tested.
- Test metric creation without air pressure (should remain optional)
- Test retrieval of metrics with air pressure data
- Test edge cases (very high/low pressure values)
- Verify backwards compatibility (existing metrics without air pressure)

## Database Considerations
- No schema changes needed (field already exists)
- Existing records will have NULL air_pressure values (acceptable)

## Deployment Notes
- This is a non-breaking change since the field is optional
- Existing API consumers can continue without changes
- New consumers can start sending air pressure data immediately after deployment
