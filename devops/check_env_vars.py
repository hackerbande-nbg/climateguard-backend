#!/usr/bin/env python3
import json
import os
import sys


def load_required_env_vars():
    """Load required environment variables from config.json"""
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        return config.get('required_env_vars', [])

    except FileNotFoundError:
        print("ERROR: config/config.json not found")
        return None
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON in config/config.json")
        return None


def check_actual_env_vars():
    """Check if required env vars exist in actual environment variables"""
    return set(os.environ.keys())


def main():
    print("Checking environment variables from config.json...")

    required_vars = load_required_env_vars()
    if required_vars is None:
        sys.exit(1)

    if not required_vars:
        print("No environment variables found in config.json")
        return

    print(f"Required environment variables: {', '.join(required_vars)}")

    env_vars_available = check_actual_env_vars()

    missing_vars = []
    for var in required_vars:
        if var not in env_vars_available:
            missing_vars.append(var)

    if missing_vars:
        print(
            f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    print("✓ All required environment variables are present")


if __name__ == "__main__":
    main()
    missing_vars = []
    for var in required_vars:
        if var not in env_vars_in_file:
            missing_vars.append(var)

    if missing_vars:
        print(
            f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    print("✓ All required environment variables are present")


if __name__ == "__main__":
    main()
