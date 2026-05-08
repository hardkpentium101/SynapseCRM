#!/usr/bin/env python3
"""Script to inspect CRM database contents with incremental sync support.

Tracks the last execution timestamp and fetches only new/updated records.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "hcpilot.db"
TIMESTAMP_FILE = Path(__file__).parent / ".last_check_timestamp"

TABLES_WITH_TS = [
    "users", "hcps", "interactions",
    "materials", "samples", "follow_ups", "audit_logs",
]

TABLES_WITHOUT_TS = [
    "interaction_materials",
]


def connect():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("   Run 'python seed.py' first to create and populate the database.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def read_last_timestamp():
    if TIMESTAMP_FILE.exists():
        return TIMESTAMP_FILE.read_text().strip()
    return None


def write_last_timestamp(ts):
    TIMESTAMP_FILE.write_text(ts)


def get_columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def print_table(conn, table_name, after_ts=None, show_all=False):
    ts_clause = ""
    params = []

    if after_ts and not show_all:
        cols = get_columns(conn, table_name)
        ts_col = None
        for col in ("created_at", "updated_at"):
            if col in cols:
                ts_col = col
                break
        if ts_col:
            ts_clause = f" WHERE {ts_col} > ?"
            params = [after_ts]
        else:
            show_all = True

    query = f"SELECT * FROM {table_name}{ts_clause}"
    cursor = conn.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    label = " (new/updated)" if after_ts and not show_all else ""
    print(f"\n{'=' * 60}")
    print(f"  {table_name.upper()}{label} ({len(rows)} rows)")
    print("=" * 60)
    print(f"Columns: {', '.join(columns)}")
    print("-" * 60)

    if not rows:
        print("  (no records)")
        return

    for row in rows:
        for col, val in zip(columns, row):
            display = val
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, (dict, list)):
                        display = json.dumps(parsed, indent=2)
                    else:
                        display = parsed
                except (json.JSONDecodeError, TypeError):
                    pass
            print(f"  {col}: {display}")
        print()


def show_summary(conn, after_ts=None):
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print("=" * 60)

    all_tables = TABLES_WITH_TS + TABLES_WITHOUT_TS
    for table in all_tables:
        try:
            cols = get_columns(conn, table)
        except Exception:
            continue

        if after_ts and "created_at" in cols:
            cursor = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE created_at > ?", (after_ts,)
            )
            label = "new/updated"
        else:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            label = "total"

        count = cursor.fetchone()[0]
        print(f"  {table:25s} {label}: {count}")


def main():
    last_ts = read_last_timestamp()

    if last_ts:
        print(f"CRM Database Incremental Inspector")
        print(f"  Database: {DB_PATH}")
        print(f"  Last check: {last_ts}")
        print(f"  Showing records created/updated after: {last_ts}\n")
    else:
        print(f"CRM Database Full Inspector")
        print(f"  Database: {DB_PATH}")
        print(f"  No previous check timestamp found. Showing all records.\n")

    conn = connect()

    for table in TABLES_WITH_TS:
        print_table(conn, table, after_ts=last_ts)

    for table in TABLES_WITHOUT_TS:
        print_table(conn, table, show_all=True)

    show_summary(conn, after_ts=last_ts)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_last_timestamp(now)
    print(f"\n  Timestamp saved: {now}")

    conn.close()
    print("Done!")


if __name__ == "__main__":
    main()
