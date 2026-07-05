import sqlite3
import json
from pathlib import Path

def get_db_connection():
    with open("config.json") as f:
        config = json.load(f)
    conn = sqlite3.connect(config["database_path"])
    conn.row_factory = sqlite3.Row  # isse hum column names se data nikal sakte hai
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def log_change(conn, entity_type, entity_id, field_name, old_value, new_value, change_summary):
    conn.execute(
        """INSERT INTO audit_log
           (entity_type, entity_id, field_name, old_value, new_value, change_summary)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (entity_type, entity_id, field_name, str(old_value), str(new_value), change_summary)
    )


def log_notification(conn, message):
    conn.execute("INSERT INTO notifications (message) VALUES (?)", (message,))