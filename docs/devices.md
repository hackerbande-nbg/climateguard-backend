# vibe code instructions
# Follow RESTful API patterns and ensure proper error handling
# Always include tag relationships in CRUD operations as per models.py requirements
# Use proper HTTP status codes and response formats
# Include input validation for enums and required fields

# Device CRUD Endpoints Implementation Plan

## Overview
Create simple CRUD (Create, Read, Update, Delete) endpoints for the Device class with basic tag relationship handling.

## Step 1: Create Device DTOs/Schemas ✅ COMPLETED
- ✅ Created `DeviceCreate` schema for POST requests
- ✅ Created `DeviceRead` schema for GET responses  
- ✅ Created `DeviceUpdate` schema for PUT/PATCH requests
- ✅ Included tag relationships in all schemas
- ✅ Added validation for enum fields (GroundCover, Orientation, Shading)
- File: `/home/andi/git/climateguard-backend/project/app/schemas.py`

## Step 2: Create Device API Routes (Direct Database Operations) ✅ COMPLETED
- ✅ `POST /api/v1/devices` - Create new device with tags
- ✅ `GET /api/v1/devices` - List all devices with basic filtering
- ✅ `GET /api/v1/devices/{device_id}` - Get specific device with tags
- ✅ `PUT /api/v1/devices/{device_id}` - Update entire device
- ✅ `DELETE /api/v1/devices/{device_id}` - Delete device
- ✅ Handle tag associations directly in route handlers
- File: `/home/andi/git/climateguard-backend/project/app/v2/routers/devices.py`

## Step 3: Add Basic Input Validation ✅ COMPLETED
- ✅ Validate enum values (GroundCover, Orientation, Shading)
- ✅ Validate required fields and data types
- ✅ Basic latitude/longitude range validation
- ✅ Ensure device name uniqueness

## Step 4: Add Error Handling ✅ COMPLETED
- ✅ Handle device not found (404)
- ✅ Handle validation errors (422)
- ✅ Handle database constraint violations (400)
- ✅ Handle duplicate device names (409)

## Step 5: Add Query Parameters Support ✅ COMPLETED
- ✅ Basic pagination (limit, offset)
- ✅ Simple filtering by enum fields
- ✅ Basic tag filtering
- ✅ Simple sorting by id, name, created_at

## Step 6: Add Response Formatting ✅ COMPLETED
- ✅ Consistent JSON response structure
- ✅ Include tag information in device responses
- ✅ Proper datetime formatting
- ✅ Include pagination metadata

## Step 7: Add Tests ✅ COMPLETED
- ✅ Basic integration tests for each endpoint
- ✅ Test CRUD operations with tags
- ✅ Test enum validation
- ✅ Test error scenarios
- ✅ Test pagination and filtering
- ✅ Test tag relationship handling in all operations
- ✅ Test duplicate device name handling
- ✅ Test device not found scenarios
- File: `/home/andi/git/climateguard-backend/test/integration/test_devices.py`

## Step 8: Add Documentation ✅ COMPLETED
- ✅ OpenAPI/Swagger documentation with detailed descriptions
- ✅ Request/response examples for all endpoints
- ✅ Enum value documentation and constraints
- ✅ Error response documentation with examples
- ✅ Tag relationship handling examples
- ✅ Parameter validation documentation
- ✅ Comprehensive API route descriptions

## Notes
- All device operations must include tag relationships per vibe code instructions
- Keep it simple - direct database operations in route handlers
- Focus on basic CRUD functionality without complex business logic
- Ensure proper tag association handling in all operations
- Pagination (limit, offset)
- Filtering by location (latitude/longitude bounds)
- Filtering by ground cover, orientation, shading
- Filtering by tags (category, tag name)
- Sorting by created_at, name, location