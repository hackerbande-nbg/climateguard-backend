import secrets
import hashlib
from typing import Tuple


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        str: 32-character alphanumeric API key
    """
    return secrets.token_urlsafe(32)[:32]


def generate_salt() -> str:
    """
    Generate a cryptographically secure random salt.

    Returns:
        str: 16-character random salt
    """
    return secrets.token_urlsafe(16)


def hash_api_key(api_key: str, salt: str) -> str:
    """
    Hash an API key with a salt using PBKDF2-HMAC-SHA256.

    Args:
        api_key (str): The API key to hash
        salt (str): The salt to use for hashing

    Returns:
        str: Hexadecimal representation of the hashed API key
    """
    return hashlib.pbkdf2_hmac(
        'sha256',
        api_key.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations for security
    ).hex()


def verify_api_key(api_key: str, stored_hash: str, salt: str) -> bool:
    """
    Verify an API key against a stored hash.

    Args:
        api_key (str): The API key to verify
        stored_hash (str): The stored hash to compare against
        salt (str): The salt used for the stored hash

    Returns:
        bool: True if the API key matches, False otherwise
    """
    computed_hash = hash_api_key(api_key, salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def generate_api_key_with_hash() -> Tuple[str, str, str]:
    """
    Generate a new API key along with its hash and salt.
    Convenience function for user registration.

    Returns:
        Tuple[str, str, str]: (api_key, hash, salt)
    """
    api_key = generate_api_key()
    salt = generate_salt()
    key_hash = hash_api_key(api_key, salt)

    return api_key, key_hash, salt


def is_valid_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key (str): The API key to validate

    Returns:
        bool: True if format is valid, False otherwise
    """
    if not api_key:
        return False

    # Check length (should be 32 characters)
    if len(api_key) != 32:
        return False

    # Check if contains only valid URL-safe characters
    # (alphanumeric plus - and _)
    valid_chars = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    return all(c in valid_chars for c in api_key)
