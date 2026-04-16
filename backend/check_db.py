#!/usr/bin/env python3
"""Script to inspect CRM database contents."""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "crm.db"


def connect():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Run 'python seed.py' first to create and populate the database.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def print_table(conn, table_name):
    cursor = conn.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    print(f"\n{'=' * 60}")
    print(f"📋 {table_name.upper()} ({len(rows)} rows)")
    print("=" * 60)
    print(f"Columns: {', '.join(columns)}")
    print("-" * 60)

    for row in rows:
        for i, (col, val) in enumerate(zip(columns, row)):
            print(f"  {col}: {val}")
        print()


def main():
    conn = connect()

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]

    print("🔍 CRM Database Inspector")
    print(f"   Database: {DB_PATH}")
    print(f"   Tables: {', '.join(tables)}")

    for table in tables:
        print_table(conn, table)

    conn.close()
    print("✅ Done!")


if __name__ == "__main__":
    main()
