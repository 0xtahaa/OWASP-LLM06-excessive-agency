"""
tools.py (fixed version)

Defines narrow, single-purpose tools instead of one generic SQL tool.

This is APPROACH A (least privilege / granular scopes):
- lookup_customer_by_id can only ever read one customer row. It has
  no way to read multiple rows, no way to read other tables, and no
  way to write anything.
- update_customer_email can only ever change ONE column (email) on
  ONE row, identified by customer_id. It cannot delete rows, cannot
  touch order_history, cannot run arbitrary SQL.

Structurally, even if a tool call were *approved*, the blast radius
of what it could do is already much smaller than the vulnerable
version's execute_sql. But approach A alone is not enough — see
policy.py for why (a tool can still be called with the WRONG
customer_id, which approach A cannot detect on its own).
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer_by_id",
            "description": "Look up a single customer's name, email, and order history by their customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The ID of the customer to look up.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_customer_email",
            "description": "Update a single customer's email address by their customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The ID of the customer whose email should be updated.",
                    },
                    "new_email": {
                        "type": "string",
                        "description": "The new email address to set.",
                    },
                },
                "required": ["customer_id", "new_email"],
            },
        },
    },
]


def lookup_customer_by_id(customer_id: int) -> str:
    """Read-only lookup of exactly one customer row. No other table, no write access."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, name, email, order_history FROM customers WHERE id = ?",
            (customer_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return f"No customer found with id {customer_id}."
        columns = ["id", "name", "email", "order_history"]
        return str(dict(zip(columns, row)))
    finally:
        conn.close()


def update_customer_email(customer_id: int, new_email: str) -> str:
    """Write access limited to exactly one column (email) on exactly one row."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE customers SET email = ? WHERE id = ?",
            (new_email, customer_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return f"No customer found with id {customer_id}. Nothing updated."
        return f"Email for customer {customer_id} updated to {new_email}."
    finally:
        conn.close()


TOOL_FUNCTIONS = {
    "lookup_customer_by_id": lookup_customer_by_id,
    "update_customer_email": update_customer_email,
}
