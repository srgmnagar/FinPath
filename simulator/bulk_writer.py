import io
import json
import psycopg2
from datetime import datetime

def get_connection(db_config: dict):
    return psycopg2.connect(**db_config)


def bulk_insert_users(conn, users: list[dict]):
    """Insert users using COPY — fastest method, no per-row overhead."""
    buf = io.StringIO()
    for u in users:
        buf.write("\t".join([
            str(u["user_id"]),
            _ts(u["signup_at"]),
            u["device_type"],
            u["country"],
            u["risk_profile"],
            _ts(u.get("activated_at")),
            _ts(u.get("first_deposit_at")),
        ]) + "\n")
    buf.seek(0)

    with conn.cursor() as cur:
        cur.copy_expert(
            """COPY users (user_id, signup_at, device_type, country, risk_profile,
                           activated_at, first_deposit_at)
               FROM STDIN WITH (FORMAT text, NULL '\\N')""",
            buf
        )
    conn.commit()


def bulk_insert_events(conn, events: list[dict], batch_size: int = 50000):
    """Insert events in batches using COPY."""
    total = len(events)
    inserted = 0

    for start in range(0, total, batch_size):
        batch = events[start: start + batch_size]
        buf = io.StringIO()
        for e in batch:
            buf.write("\t".join([
                str(e["user_id"]),
                e["event_type"],
                _ts(e["timestamp"]),
                json.dumps(e["properties"]),
                e["session_id"],
            ]) + "\n")
        buf.seek(0)

        with conn.cursor() as cur:
            cur.copy_expert(
                """COPY events (user_id, event_type, timestamp, properties, session_id)
                   FROM STDIN WITH (FORMAT text, NULL '\\N')""",
                buf
            )
        conn.commit()
        inserted += len(batch)
        print(f"  Events: {inserted:,} / {total:,} inserted", end="\r")

    print()


def _ts(val) -> str:
    """Format timestamp or NULL for COPY."""
    if val is None:
        return "\\N"
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return str(val)
