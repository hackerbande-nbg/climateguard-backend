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

# Authentication Implementation Plan

## Step 9: Implement Basic API Key Authentication 🔄 IN PROGRESS

### Phase 9.1: Database Schema for Authentication ✅ COMPLETED
- ✅ Create `User` model with fields:
  - `user_id`: Primary key
  - `username`: Unique username (manually created by admin)
  - `email`: User email (optional, can be added during registration)
  - `api_key_hash`: Hashed and salted API key (null until user completes registration)
  - `api_key_salt`: Salt for the API key (null until user completes registration)
  - `is_active`: Boolean flag for account status (default: false)
  - `is_registered`: Boolean flag indicating if user has completed registration (default: false)
  - `created_at`: Account creation timestamp (set by admin)
  - `registered_at`: Registration completion timestamp (set during registration)
  - `last_login`: Last authentication timestamp
- ✅ Create `UserTagLink` for user-tag relationships (following vibe code instructions)
- [ ] Add Alembic migration for user tables
- File: `/home/andi/git/climateguard-backend/project/app/models.py`

### Phase 9.2: Authentication Utilities ✅ COMPLETED
- ✅ Create `auth.py` utility module with:
  - `generate_api_key()`: Generate secure random API key
  - `hash_api_key(api_key: str, salt: str)`: Hash API key with salt
  - `verify_api_key(api_key: str, hash: str, salt: str)`: Verify API key
  - `generate_salt()`: Generate cryptographic salt
- ✅ Use `secrets` module for secure random generation
- ✅ Use `hashlib.pbkdf2_hmac` for password hashing
- File: `/home/andi/git/climateguard-backend/project/app/auth.py`

### Phase 9.3: Authentication Schemas ✅ COMPLETED
- ✅ Create `UserRegistrationRequest` schema for user self-registration:
  - `username`: Must match existing database entry
  - `email`: Optional email address
- ✅ Create `UserRead` schema for user information (exclude sensitive data)
- ✅ Create `ApiKeyResponse` schema for API key generation
- ✅ Add authentication-related error schemas
- File: `/home/andi/git/climateguard-backend/project/app/schemas.py`

### Phase 9.4: Authentication Dependencies ✅ COMPLETED
- ✅ Create `get_current_user()` dependency function:
  - Extract API key from `X-API-Key` header or `Authorization: Bearer` header
  - Query database for user with matching API key hash
  - Verify user is active and registered
  - Return user object or raise 401 Unauthorized
- ✅ Create `require_auth()` dependency wrapper
- ✅ Handle authentication errors with proper HTTP responses
- ✅ Add optional authentication dependency for mixed endpoints
- ✅ Include proper logging for security auditing
- File: `/home/andi/git/climateguard-backend/project/app/dependencies.py`

### Phase 9.5: User Management Endpoints ✅ COMPLETED
- ✅ Create `/auth/register` endpoint (POST):
  - **Modified Process**: User must already exist in database (pre-created by admin)
  - Verify username exists in database
  - Check user is not already registered (`is_registered` = false)
  - Generate and return API key (only shown once)
  - Hash and salt API key before storing
  - Update user record: set `is_registered` = true, `is_active` = true, `registered_at` = now
- ✅ Create `/auth/users/me` endpoint (GET):
  - Return current user information with tags
  - Require authentication
- ✅ Create `/auth/regenerate-key` endpoint (POST):
  - Generate new API key for existing user
  - Invalidate old API key
  - Require authentication
- ✅ **No separate onboarding endpoint** - registration handles the complete flow
- ✅ Include proper logging for security auditing
- ✅ Follow vibe code instructions for tag relationships
- File: `/home/andi/git/climateguard-backend/project/app/v2/routers/auth.py`

### Phase 9.6: Apply Authentication to Existing Endpoints ✅ COMPLETED
- ✅ **Public Endpoints (No Authentication Required):**
  - `GET /v2/metrics` - Read sensor metrics
  - `GET /v2/metrics?*` - Read metrics with filters
  - `GET /v2/ping` - Health check
  - `POST /v2/auth/register` - User registration (public but requires pre-existing username)
- ✅ **Protected Endpoints (Authentication Required):**
  - `POST /v2/metrics` - Create new metrics
  - `GET /v2/devices` - List devices
  - `GET /v2/devices/{id}` - Get specific device
  - `POST /v2/devices` - Create device
  - `PUT /v2/devices/{id}` - Update device
  - `DELETE /v2/devices/{id}` - Delete device
  - `GET /v2/auth/users/me` - Get user information
  - `POST /v2/auth/regenerate-key` - Regenerate API key
- ✅ Add `Depends(require_auth)` to protected endpoints
- ✅ Update OpenAPI documentation with security schemes
- ✅ Add authentication warnings to endpoint descriptions
- Files: 
  - `/home/andi/git/climateguard-backend/project/app/v2/routers/devices.py`
  - `/home/andi/git/climateguard-backend/project/app/v2/routers/metrics.py`
  - `/home/andi/git/climateguard-backend/project/app/v2/api.py`

### Phase 9.7: Error Handling and Security ✅ COMPLETED
- ✅ Implement proper error responses:
  - 401 Unauthorized: Missing or invalid API key with detailed error codes
  - 403 Forbidden: Valid user but not active/registered with specific messages
  - 404 Not Found: Username not found during registration with clear guidance
  - 409 Conflict: User already registered with appropriate error code
  - 422 Unprocessable Entity: Invalid input format with validation details
- ✅ Add rate limiting considerations (documentation)
- ✅ Implement secure headers (X-API-Key validation with proper error codes)
- ✅ Add API key format validation (length, characters, security patterns)
- ✅ Log authentication attempts (success/failure) with appropriate detail levels
- ✅ Enhanced input validation for usernames and emails
- ✅ Security headers in error responses with error codes
- ✅ Comprehensive API key format validation including security checks
- Files:
  - `/home/andi/git/climateguard-backend/project/app/dependencies.py`
  - `/home/andi/git/climateguard-backend/project/app/v2/routers/auth.py`
  - `/home/andi/git/climateguard-backend/project/app/auth.py`

### Phase 9.8: Testing Authentication 🔄 IN PROGRESS

#### Authentication Testing Plan

**Current Status Analysis:**
- ✅ All device endpoints now require authentication (`Depends(require_auth)`)
- ✅ POST metrics endpoint requires authentication
- ✅ GET metrics and ping endpoints remain public
- ✅ Authentication registration endpoint is public
- ⚠️ Current tests will fail because they don't include auth headers

**Test User Setup:**
- **Username**: `test_user` (from .env: TEST_USER_NAME)
- **API Key**: `aslkdhl2389042230asdhl` (from .env: TEST_USER_PW)
- **Email**: `test_user@example.com`
- **Status**: Pre-created and registered via bootstrap script

**Required Actions:**

#### 9.8.1: Create Bootstrap Script ✅ COMPLETED
- ✅ Create script to add test user to database
- ✅ Read database configuration from `.env` file
- ✅ Connect to PostgreSQL database specified in environment
- ✅ Insert test user record: `username='test_user'`, `is_active=false`, `is_registered=false`
- ✅ Register test user with predefined API key from .env
- ✅ Verify user creation and registration
- File: `/home/andi/git/climateguard-backend/devops/bootstrap_test_user.py`

#### 9.8.2: Create Authentication Test Utilities ✅ COMPLETED
- ✅ Helper function to register test user and get API key
- ✅ Helper function to add auth headers to requests
- ✅ Helper function to create authenticated HTTP client
- ✅ Read test user credentials from .env file
- ✅ Support both X-API-Key and Authorization Bearer headers
- File: `/home/andi/git/climateguard-backend/test/utils/auth_helpers.py`

#### 9.8.3: Update Existing Integration Tests ⏳ NEXT
- [ ] **Critical**: Update ALL device endpoint tests to include authentication
  - **Affected file**: `/home/andi/git/climateguard-backend/test/integration/test_devices.py`
  - Add authentication headers to all device CRUD operations
  - Test authentication failure scenarios (401 responses)
- [ ] Update POST metrics tests to include authentication  
  - **Affected file**: `/home/andi/git/climateguard-backend/test/integration/test_metrics.py`
- [ ] Verify public endpoints work without authentication (GET metrics, ping)

#### 9.8.4: Create Authentication-Specific Tests ⏳ NEXT
- [ ] Test user registration flow (with pre-existing username)
- [ ] Test registration with non-existent username (should fail)
- [ ] Test API key validation and format checking
- [ ] Test invalid API key scenarios (401 responses)
- [ ] Test user information retrieval (`/auth/users/me`)
- [ ] Test already registered user trying to register again (409 conflict)
- [ ] Test API key regeneration
- File: `/home/andi/git/climateguard-backend/test/integration/test_auth.py`

**Bootstrap Script Requirements:**
```bash
# Run bootstrap script to setup test user
python devops/bootstrap_test_user.py

# Output shows test user credentials for integration tests
```

**Test Authentication Flow:**
1. **Setup**: Run bootstrap script to create and register test user in database
2. **Tests Use**: Predefined API key from .env for authenticated requests  
3. **Usage**: Tests use API key in `X-API-Key` header for protected endpoints
4. **Verification**: Tests verify protected endpoints work with auth, fail without auth

**Expected Test Behavior Changes:**
- **Device tests**: All will need `X-API-Key: <api_key>` header
- **Metrics tests**: POST will need auth header, GET remains public
- **New auth tests**: Registration, API key management, error scenarios

**Authentication Headers Format:**
```python
headers = {
    "X-API-Key": "aslkdhl2389042230asdhl"  # Test user's API key from .env
}
# OR
headers = {
    "Authorization": "Bearer aslkdhl2389042230asdhl"
}
```

### Phase 9.9: Documentation Updates
- [ ] Update OpenAPI documentation:
  - Add security scheme for API key authentication
  - Document authentication requirements for each endpoint
  - Add authentication examples in endpoint documentation
- [ ] Create authentication guide:
  - Admin process for pre-creating users
  - How users complete registration to get API key
  - How to use API key in requests
  - API key best practices
- [ ] Update README with authentication information

### Phase 9.10: Database Migration and Seed Data  
- [ ] Create Alembic migration script for User tables
- [ ] Add production seed data script for initial admin user
- [ ] Update deployment scripts to run migrations
- [ ] Test migration on clean database

## Implementation Guidelines

### Modified Registration Process
1. **Admin Creates User**: Manually insert user record with `username`, `user_id`, `is_active=false`, `is_registered=false`
2. **User Self-Registers**: POST to `/auth/register` with their assigned username
3. **System Validates**: Check username exists and is not already registered
4. **API Key Generated**: Create and return API key, update user record
5. **User Active**: User can now access protected endpoints with API key

### Security Best Practices
- **API Key Storage**: Never store plaintext API keys in database
- **Salt Generation**: Use cryptographically secure random salt for each user
- **Hash Algorithm**: Use PBKDF2 with SHA-256, minimum 100,000 iterations
- **API Key Format**: Generate 32-character alphanumeric keys
- **Headers**: Support both `X-API-Key: <key>` and `Authorization: Bearer <key>`
- **User Validation**: Always verify user is both active and registered

### Database Design Principles
- Follow existing patterns from Device/Tag models
- Include tag relationships for users (per vibe code instructions)
- Use proper foreign key constraints
- Add appropriate indexes for performance
- Pre-created users have null API key fields until registration

### Error Response Format
```json
{
  "detail": "Authentication required",
  "error_code": "AUTHENTICATION_REQUIRED", 
  "status_code": 401
}
```

### Registration Flow Example
```python
# Admin manually creates user in database
INSERT INTO user (username, is_active, is_registered) 
VALUES ('john_doe', false, false);

# User registers themselves
POST /v2/auth/register
{
  "username": "john_doe",
  "email": "john@example.com"  # optional
}

# Response includes API key (shown only once)
{
  "user_id": 1,
  "username": "john_doe", 
  "api_key": "abcd1234...",  # 32-char key
  "message": "Registration complete. Save your API key - it won't be shown again."
}
```

### Test Authentication Requirements
- **ALL device endpoint tests** need authentication headers
- **POST metrics tests** need authentication headers  
- **GET metrics tests** should work without authentication (public)
- **Ping endpoint tests** should work without authentication (public)
- **Registration tests** should work without authentication (public but requires pre-existing username)
- Create helper functions to reduce test code duplication

## Implementation Priority
1. **IMMEDIATE**: Update existing test cases to use authentication
2. **NEXT**: Create comprehensive authentication tests
3. **LATER**: Documentation and migration scripts

## Notes
- All user operations must include tag relationships per vibe code instructions
- Keep authentication simple - no complex RBAC for now
- Focus on API key authentication, not session-based auth
- Ensure backward compatibility during implementation (metrics GET endpoints remain public)
- Plan for future enhancements (roles, permissions, etc.)
- Admin tooling needed for user management outside the API
- Single registration endpoint handles the complete onboarding flow
- Test user API key is fixed for consistent testing
- Bootstrap script should be idempotent (safe to run multiple times)
