import argparse
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from pathlib import Path
from user_factory import generate_users
from flow_engine import simulate_user
from bulk_writer import get_connection, bulk_insert_users, bulk_insert_events

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")
DB_HOST=os.getenv("DB_HOST")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

DB_CONFIG = {
    "host":     DB_HOST,
    "port":     5432,
    "dbname":   DB_NAME,       
    "user":    DB_USER,      
    "password": DB_PASSWORD,             
}

def main():
    parser = argparse.ArgumentParser(description="FinPath simulator")
    parser.add_argument("--users",  type=int, default=250_000,
                        help="Number of users to simulate (default: 250000)")
    parser.add_argument("--seed",   type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    import random
    random.seed(args.seed)

    print(f"\nFinPath Simulator")
    print(f"{'─' * 40}")
    print(f"Users:    {args.users:,}")
    print(f"Seed:     {args.seed}")
    print(f"{'─' * 40}\n")

    # ── Step 1: Generate users ────────────────────────────────────────────────
    t0 = time.time()
    print(f"[1/4] Generating {args.users:,} user profiles...")
    users = generate_users(args.users)
    print(f"      Done in {time.time()-t0:.1f}s\n")

    # ── Step 2: Simulate journeys ─────────────────────────────────────────────
    t1 = time.time()
    print(f"[2/4] Simulating user journeys...")
    all_events = []
    updated_users = []

    for i, user in enumerate(users):
        updated_user, events = simulate_user(user)
        updated_users.append(updated_user)
        all_events.extend(events)

        if (i + 1) % 10_000 == 0:
            print(f"      {i+1:,} / {args.users:,} users — {len(all_events):,} events so far")

    elapsed = time.time() - t1
    avg_events = len(all_events) / args.users
    print(f"      Done in {elapsed:.1f}s")
    print(f"      Total events: {len(all_events):,}")
    print(f"      Avg events/user: {avg_events:.1f}\n")

    # ── Step 3: Connect to DB ─────────────────────────────────────────────────
    print(f"[3/4] Connecting to PostgreSQL...")
    try:
        conn = get_connection(DB_CONFIG)
        print(f"      Connected to '{DB_CONFIG['dbname']}'\n")
    except Exception as e:
        print(f"      ERROR: {e}")
        print(f"\n      Check DB_CONFIG in run.py and make sure PostgreSQL is running.")
        sys.exit(1)

    # ── Step 4: Bulk write ────────────────────────────────────────────────────
    t3 = time.time()
    print(f"[4/4] Writing to database...")

    print(f"  Users: inserting {len(updated_users):,}...")
    bulk_insert_users(conn, updated_users)
    print(f"  Users: done\n")

    print(f"  Events: inserting {len(all_events):,} in batches of 50,000...")
    bulk_insert_events(conn, all_events)

    conn.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    total_time = time.time() - t0
    print(f"\n{'─' * 40}")
    print(f"Simulation complete!")
    print(f"  Users inserted:  {len(updated_users):,}")
    print(f"  Events inserted: {len(all_events):,}")
    print(f"  Total time:      {total_time:.1f}s")
    print(f"  Throughput:      {len(all_events)/total_time:,.0f} events/sec")
    print(f"{'─' * 40}\n")

    # ── Quick sanity check ────────────────────────────────────────────────────
    print("Quick DB check:")
    conn2 = get_connection(DB_CONFIG)
    with conn2.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        print(f"  users table:  {cur.fetchone()[0]:,} rows")
        cur.execute("SELECT COUNT(*) FROM events")
        print(f"  events table: {cur.fetchone()[0]:,} rows")
        cur.execute("""
            SELECT event_type, COUNT(*) as cnt
            FROM events GROUP BY event_type
            ORDER BY cnt DESC LIMIT 10
        """)
        print(f"\n  Top 10 event types:")
        for row in cur.fetchall():
            print(f"    {row[0]:<35} {row[1]:>10,}")
    conn2.close()
    print()


if __name__ == "__main__":
    main()
