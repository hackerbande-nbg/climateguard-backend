#!/usr/bin/env python3
"""
Bootstrap script to create and register test user in database for integration testing.

This script:
1. Reads database configuration from .env file
2. Connects to PostgreSQL database
3. Creates test user with predefined credentials
4. Registers the test user with predefined API key
5. Handles existing user gracefully
"""

from auth import hash_api_key, generate_salt
from dotenv import load_dotenv
import os
import sys
import asyncio
import asyncpg
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / '.env')

# Import auth utilities for API key generation

# Test user configuration from environment variables
TEST_USER_CONFIG = {
    'username': os.getenv('TEST_USER_NAME', 'test_user'),
    'email': f"{os.getenv('TEST_USER_NAME', 'test_user')}@example.com",
    'api_key': os.getenv('TEST_USER_PW'),
    'is_active': False,
    'is_registered': False,
    'created_at': datetime.utcnow()
}

DB_PORT = int(os.getenv('DB_PORT'))  # Default to 5432 if not set


async def get_database_connection():
    """Create database connection from environment variables"""
    print(DB_PORT)
    # Read database configuration from .env
    db_config = {
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PW'),
        'database': os.getenv('POSTGRES_DB'),
        'host': os.getenv('POSTGRES_DNS', 'localhost'),
        'port': DB_PORT
    }

    print(
        f"🔌 Connecting to database: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    try:
        connection = await asyncpg.connect(
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            host=db_config['host'],
            port=db_config['port']
        )
        print("✅ Database connection successful")
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


async def check_user_exists(connection, username):
    """Check if user already exists in database"""

    query = "SELECT user_id, username, is_registered, is_active FROM \"user\" WHERE username = $1"

    try:
        result = await connection.fetchrow(query, username)
        return result
    except Exception as e:
        print(f"❌ Error checking user existence: {e}")
        return None


async def create_test_user(connection):
    """Create test user in database"""

    insert_query = """
    INSERT INTO "user" (username, email, is_active, is_registered, created_at)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING user_id, username
    """

    try:
        result = await connection.fetchrow(
            insert_query,
            TEST_USER_CONFIG['username'],
            TEST_USER_CONFIG['email'],
            TEST_USER_CONFIG['is_active'],
            TEST_USER_CONFIG['is_registered'],
            TEST_USER_CONFIG['created_at']
        )

        print("✅ Test user created successfully:")
        print(f"   User ID: {result['user_id']}")
        print(f"   Username: {result['username']}")

        return result

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        sys.exit(1)


async def register_test_user(connection, user_id):
    """Register test user with predefined API key"""

    # Generate salt and hash for the predefined API key
    salt = generate_salt()
    api_key_hash = hash_api_key(TEST_USER_CONFIG['api_key'], salt)

    update_query = """
    UPDATE "user"
    SET api_key_hash = $1,
        api_key_salt = $2,
        is_active = true,
        is_registered = true,
        registered_at = $3
    WHERE user_id = $4
    RETURNING user_id, username, is_registered, is_active
    """

    try:

        result = await connection.fetchrow(
            update_query,
            api_key_hash,
            salt,
            datetime.utcnow(),
            user_id
        )

        print("✅ Test user registered successfully:")
        print(f"   User ID: {result['user_id']}")
        print(f"   Username: {result['username']}")
        print(f"   API Key: {TEST_USER_CONFIG['api_key']}")
        print(f"   Active: {result['is_active']}")
        print(f"   Registered: {result['is_registered']}")

        return result

    except Exception as e:
        print(f"❌ Error registering test user: {e}")
        sys.exit(1)


async def main():
    """Main bootstrap function"""

    print("🚀 Bootstrap Test User Script")

    # Connect to database
    connection = await get_database_connection()

    try:
        # Check if test user already exists
        existing_user = await check_user_exists(connection, TEST_USER_CONFIG['username'])

        if existing_user:
            print(
                f"⚠️  Test user '{TEST_USER_CONFIG['username']}' already exists:")
            if existing_user['is_registered']:
                print("   User is already registered and ready for testing")
            else:
                print("   User exists but not registered - registering now...")
                await register_test_user(connection, existing_user['user_id'])
        else:
            # Create test user
            print(f"📝 Creating test user '{TEST_USER_CONFIG['username']}'...")
            created_user = await create_test_user(connection)

            # Register the test user
            print("🔐 Registering test user...")
            await register_test_user(connection, created_user['user_id'])

        print("\n✅ Bootstrap completed successfully!")

    finally:
        await connection.close()
        print("🔌 Database connection closed")


if __name__ == "__main__":
    # Run the bootstrap script
    asyncio.run(main())
