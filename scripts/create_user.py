"""
Bootstrap CLI for creating user accounts.

Prompts for the password interactively via getpass - it is never accepted as a
command-line argument (which would leak into shell history and process lists)
and never stored anywhere in plaintext.

Usage:
    python scripts/create_user.py
    python scripts/create_user.py --list
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import store  # noqa: E402
from auth.security import hash_password  # noqa: E402

VALID_ROLES = ["doctor", "nurse", "admin"]
MIN_PASSWORD_LENGTH = 8


def prompt_password() -> str:
    """Ask for a password twice and verify the two entries match"""
    while True:
        password = getpass.getpass("Password: ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            continue

        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match. Try again.")
            continue

        return password


def create() -> int:
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return 1

    if store.get_user(username) is not None:
        print(f"User '{username}' already exists.")
        return 1

    role = input(f"Role {VALID_ROLES} [doctor]: ").strip() or "doctor"
    if role not in VALID_ROLES:
        print(f"Invalid role '{role}'. Must be one of: {', '.join(VALID_ROLES)}")
        return 1

    password = prompt_password()

    try:
        user = store.create_user(username, hash_password(password), role)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Created user '{user.username}' with role '{user.role}'.")
    return 0


def show_users() -> int:
    users = store.list_users()
    if not users:
        print("No users yet. Run this script without --list to create one.")
        return 0

    print(f"{'USERNAME':<24} {'ROLE':<12} STATUS")
    for user in users:
        print(
            f"{user.username:<24} {user.role:<12} "
            f"{'disabled' if user.disabled else 'active'}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage API user accounts")
    parser.add_argument(
        "--list", action="store_true", help="List existing users instead of creating one"
    )
    args = parser.parse_args()

    store.init_db()
    return show_users() if args.list else create()


if __name__ == "__main__":
    sys.exit(main())
