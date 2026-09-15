import sqlite3
import csv
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "port_operations.db"

def get_db_connection():
    """Returns a sqlite3 connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates SQLite tables and populates them from CSV datasets if empty."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Vessels Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vessels (
            vessel_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            eta TEXT NOT NULL,
            current_port TEXT NOT NULL,
            destination TEXT NOT NULL,
            cargo_type TEXT NOT NULL,
            container_count INTEGER NOT NULL,
            priority TEXT NOT NULL,
            assigned_berth TEXT,
            estimated_waiting_time_hrs REAL DEFAULT 0.0,
            length_m REAL NOT NULL,
            draft_m REAL NOT NULL,
            status TEXT NOT NULL
        );
    """)

    # 2. Berths Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS berths (
            berth_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            max_ship_length REAL NOT NULL,
            max_draft REAL NOT NULL,
            capacity_teu INTEGER NOT NULL,
            current_occupancy REAL NOT NULL,
            status TEXT NOT NULL,
            zone TEXT NOT NULL
        );
    """)

    # 3. Cranes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cranes (
            crane_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            berth_id TEXT NOT NULL,
            handling_rate_teu_hr INTEGER NOT NULL,
            status TEXT NOT NULL,
            assigned_vessel_id TEXT
        );
    """)

    # 4. Disruptions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disruptions (
            disruption_id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            affected_target TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            start_time TEXT NOT NULL,
            expected_duration_hrs INTEGER NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );
    """)

    # 5. Assignments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_id TEXT NOT NULL,
            berth_id TEXT NOT NULL,
            assigned_cranes TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL,
            reason TEXT
        );
    """)

    # 6. Operations Plan Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operations_plan (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_block TEXT NOT NULL,
            vessel_id TEXT NOT NULL,
            berth_id TEXT NOT NULL,
            cranes TEXT NOT NULL,
            action TEXT NOT NULL,
            priority TEXT NOT NULL,
            congestion_risk TEXT NOT NULL,
            expected_impact TEXT NOT NULL
        );
    """)

    conn.commit()

    # Seed data from CSV if tables are empty
    _seed_table_from_csv(conn, "vessels", DATA_DIR / "vessels.csv")
    _seed_table_from_csv(conn, "berths", DATA_DIR / "berths.csv")
    _seed_table_from_csv(conn, "cranes", DATA_DIR / "cranes.csv")
    _seed_table_from_csv(conn, "disruptions", DATA_DIR / "disruptions.csv")

    conn.close()

def _seed_table_from_csv(conn, table_name: str, csv_path: Path):
    """Helper to load CSV into table if empty using standard library csv module."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0 and csv_path.exists():
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            if columns:
                placeholders = ", ".join(["?"] * len(columns))
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                for row in reader:
                    cursor.execute(sql, [row[col] for col in columns])
        conn.commit()

# Helper queries
def fetch_all(query: str, params: tuple = ()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def fetch_one(query: str, params: tuple = ()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def execute_query(query: str, params: tuple = ()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
