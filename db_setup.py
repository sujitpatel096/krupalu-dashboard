"""
Krupalu Creation - database setup
Creates the local SQLite database and all tables from config.json.
Run once: python db_setup.py
Safe to re-run - uses CREATE TABLE IF NOT EXISTS.
"""

import json
import sqlite3
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_connection(config):
    db_path = Path(__file__).parent / config["database_path"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    gst_number TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS garment_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    length_per_piece_m REAL
);

CREATE TABLE IF NOT EXISTS fabric_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fabric_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS inward_challans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id INTEGER NOT NULL REFERENCES parties(id),
    inward_challan_number TEXT NOT NULL,
    date_received TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS inward_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inward_challan_id INTEGER NOT NULL REFERENCES inward_challans(id),
    fabric_name TEXT NOT NULL,
    garment_type_id INTEGER REFERENCES garment_types(id),
    design_count INTEGER DEFAULT 0,
    meters_given REAL NOT NULL,
    pieces_ordered INTEGER,
    rate_per_meter REAL,
    length_per_piece_used REAL,
    production_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inward_item_id INTEGER NOT NULL REFERENCES inward_items(id),
    outward_challan_number TEXT NOT NULL,
    meters_delivered REAL NOT NULL,
    delivery_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_takkas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id),
    meters REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS fabric_damage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inward_item_id INTEGER NOT NULL REFERENCES inward_items(id),
    damage_meters REAL NOT NULL,
    stage TEXT NOT NULL,
    reported_by TEXT,
    note TEXT,
    logged_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id),
    base_amount REAL NOT NULL,
    gst_percent REAL NOT NULL DEFAULT 0,
    gst_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL,
    amount_paid REAL NOT NULL DEFAULT 0,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS payment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    paid_amount REAL NOT NULL,
    paid_date TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_summary TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reminders_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    sent_at TEXT NOT NULL DEFAULT (datetime('now')),
    message_status TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def create_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def seed_garment_types(conn, config):
    cur = conn.cursor()
    for gt in config["default_garment_types"]:
        cur.execute(
            "INSERT OR IGNORE INTO garment_types (name, length_per_piece_m) VALUES (?, ?)",
            (gt["name"], gt["length_per_piece_m"]),
        )
    conn.commit()

def seed_fabric_master(conn, config):
    cur = conn.cursor()
    for name in config.get("fabric_master_list", []):
        cur.execute(
            "INSERT OR IGNORE INTO fabric_master (fabric_name) VALUES (?)",
            (name,)
        )
    conn.commit()


def main():
    config = load_config()
    conn = get_connection(config)
    create_schema(conn)
    seed_garment_types(conn, config)
    seed_fabric_master(conn, config)

    # Purane database me naye columns add karna (agar pehle se na ho)
    try:
        conn.execute("ALTER TABLE inward_items ADD COLUMN fabric_width_inches INTEGER")
    except Exception:
        pass
    conn.commit()

    try:
        conn.execute("ALTER TABLE inward_items ADD COLUMN total_takka INTEGER")
    except Exception:
        pass
    conn.commit()

    conn.close()
    print("Database ready at", config["database_path"])


if __name__ == "__main__":
    main()