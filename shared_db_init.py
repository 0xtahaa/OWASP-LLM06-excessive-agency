"""
shared_db_init.py

Reusable function to create the dummy customer database.
This file lives once at the repo root and is imported by both
vulnerable/setup_db.py and fixed/setup_db.py, so the *data* is
guaranteed to be identical across both demos, while each demo
still gets its own, independent database FILE.

Why separate files instead of one shared shop.db?
Because the vulnerable agent can modify or delete rows. If both
versions pointed at the same physical file, running the vulnerable
demo first would silently corrupt the starting state for the fixed
demo afterwards. Separate files = fair, reproducible comparison.
"""

import sqlite3
import os


def create_database(db_path: str) -> None:
    """Create a fresh customers database at the given path."""

    # Start from a clean slate every time, so demo runs are reproducible.
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            order_history TEXT NOT NULL
        )
        """
    )

    # Dummy data only. No real people, no real emails.
    dummy_customers = [
        (1, "Anna Sample", "anna.sample@example.com", "Order #1001: Laptop Stand"),
        (2, "Ben Example", "ben.example@example.com", "Order #1002: USB-C Cable"),
        (3, "Clara Testuser", "clara.testuser@example.com", "Order #1003: Mechanical Keyboard"),
    ]

    cursor.executemany(
        "INSERT INTO customers (id, name, email, order_history) VALUES (?, ?, ?, ?)",
        dummy_customers,
    )

    conn.commit()
    conn.close()
    print(f"Database created at {db_path} with {len(dummy_customers)} dummy customers.")
