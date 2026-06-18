"""
setup_db.py (vulnerable version)

Creates this demo's own, isolated copy of the dummy customer database.
Run this before running agent.py:
    python setup_db.py
"""

import os
import sys

# Import the shared creation logic from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_db_init import create_database

DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")

if __name__ == "__main__":
    create_database(DB_PATH)
