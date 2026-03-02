#!/usr/bin/env python3
"""
Build script for Royals Concession Intelligence Platform.
Loads all CSV data, enriches it, and creates the SQLite database.

Usage:
    python data_foundation/build_all.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_foundation.load_data import load_all_data


def main():
    print("=" * 60)
    print("  Royals Concession Intel - Data Build")
    print("=" * 60)
    print()

    start = time.time()
    stats = load_all_data()
    elapsed = time.time() - start

    print()
    print("-" * 60)
    print("  BUILD COMPLETE")
    print("-" * 60)
    print(f"  Transactions loaded : {stats['total_rows']:,}")
    print(f"  Rows skipped        : {stats['skipped_rows']:,}")
    print(f"  Games in schedule   : {stats['games_count']}")
    print(f"  Games with POS data : {stats['games_with_data']}")
    print(f"  Total est. revenue  : ${stats['total_revenue']:,.2f}")
    print(f"  Database path       : {stats['db_path']}")
    print(f"  Build time          : {elapsed:.1f}s")
    print("-" * 60)


if __name__ == "__main__":
    main()
