# create_migration.py - Migrate from SQLite → PostgreSQL (SAFE & ROBUST)
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
import sys
from datetime import datetime
import shutil

# ==================== CONFIGURATION ====================
SQLITE_DB = os.getenv("PRINTERS_DB_FILE", "printers.db")

POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Thiza16321401%40@localhost:5432/printers"
)

if not POSTGRES_URL:
    print("❌ ERROR: DATABASE_URL environment variable is not set!")
    print("   Example: export DATABASE_URL=postgresql://user:password@localhost:5432/printers")
    sys.exit(1)


# ==================== POSTGRESQL SCHEMA (FULLY COMPATIBLE) ====================
POSTGRES_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS printers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    ip TEXT UNIQUE NOT NULL,
    location TEXT,
    department TEXT,
    model TEXT,
    serial_number TEXT,
    purchase_date TEXT,
    warranty_expiry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS printer_states (
    id SERIAL PRIMARY KEY,
    printer_ip TEXT NOT NULL REFERENCES printers(ip) ON DELETE CASCADE,
    status TEXT NOT NULL,
    response_time REAL,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    printer_ip TEXT NOT NULL REFERENCES printers(ip) ON DELETE CASCADE,
    type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS print_jobs (
    id SERIAL PRIMARY KEY,
    job_id TEXT NOT NULL,
    printer_ip TEXT NOT NULL REFERENCES printers(ip) ON DELETE CASCADE,
    username TEXT NOT NULL,
    document_name TEXT NOT NULL,
    pages INTEGER NOT NULL,
    color_pages INTEGER DEFAULT 0,
    duplex_pages INTEGER DEFAULT 0,
    job_size INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    cost REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS printer_details (
    id SERIAL PRIMARY KEY,
    printer_ip TEXT UNIQUE NOT NULL REFERENCES printers(ip) ON DELETE CASCADE,
    model TEXT,
    serial_number TEXT,
    firmware TEXT,
    department TEXT,
    maintenance_date TEXT,
    next_maintenance TEXT,
    supplies_json TEXT,
    counters_json TEXT,
    status_json TEXT,
    printer_type TEXT,
    cost_per_page REAL DEFAULT 0.05,
    color_cost_per_page REAL DEFAULT 0.15
);

CREATE TABLE IF NOT EXISTS maintenance_logs (
    id SERIAL PRIMARY KEY,
    printer_ip TEXT NOT NULL REFERENCES printers(ip) ON DELETE CASCADE,
    maintenance_type TEXT NOT NULL,
    description TEXT,
    technician TEXT,
    cost REAL DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_maintenance TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    target TEXT,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_printers_ip ON printers(ip);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_print_jobs_timestamp ON print_jobs(timestamp);
CREATE INDEX IF NOT EXISTS idx_print_jobs_printer_ip ON print_jobs(printer_ip);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
"""

# ==================== BOOLEAN COLUMNS ====================
# All columns that are BOOLEAN in PostgreSQL
BOOLEAN_COLUMNS = {
    "users": ["is_active"],
    "printers": ["is_active"],
    "alerts": ["acknowledged", "resolved"]
}

def migrate():
    print(f"🚀 Starting migration at {datetime.now()}")
    print(f"SQLite DB: {SQLITE_DB}")
    print(f"PostgreSQL: {'********@' + POSTGRES_URL.split('@')[-1] if '@' in POSTGRES_URL else 'hidden'}")

    sqlite_conn = None
    pg_conn = None

    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()

        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(POSTGRES_URL)
        pg_cur = pg_conn.cursor()

        # Create schema
        print("📦 Creating schema in PostgreSQL...")
        pg_cur.execute(POSTGRES_SCHEMA)
        pg_conn.commit()

        # Tables to migrate (order matters for foreign keys)
        tables = [
            "users",
            "printers",
            "printer_states",
            "printer_details",
            "alerts",
            "print_jobs",
            "maintenance_logs",
            "audit_logs"
        ]

        total_migrated = 0

        for table in tables:
            print(f"\n➡️ Migrating {table}...", end=" ")

            sqlite_cur.execute(f"SELECT COUNT(*) as c FROM {table}")
            count = sqlite_cur.fetchone()["c"]
            if count == 0:
                print("empty")
                continue

            sqlite_cur.execute(f"SELECT * FROM {table}")
            rows = sqlite_cur.fetchall()
            columns = [desc[0] for desc in sqlite_cur.description]

            # Convert rows to tuples with BOOLEAN casting
            data = []
            for row in rows:
                new_row = []
                for col in columns:
                    val = row[col]
                    if table in BOOLEAN_COLUMNS and col in BOOLEAN_COLUMNS[table]:
                        val = bool(val)
                    new_row.append(val)
                data.append(tuple(new_row))

            # Build INSERT statement
            cols = ",".join(columns)
            insert_sql = f"INSERT INTO {table} ({cols}) VALUES %s ON CONFLICT DO NOTHING"
            execute_values(pg_cur, insert_sql, data, page_size=1000)

            pg_conn.commit()

            migrated = len(data)
            total_migrated += migrated
            print(f"{migrated} rows")

        # Migration summary
        print(f"\n✅ Migration completed successfully!")
        print(f"Total records migrated: {total_migrated:,}")
        print("Schema and indexes created.")
        print("You can now switch your app to PostgreSQL!")

        # Backup SQLite
        backup_name = f"printers_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(SQLITE_DB, backup_name)
        print(f"SQLite backup saved: {backup_name}")

        return True

    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        if pg_conn:
            pg_conn.rollback()
        return False

    finally:
        if sqlite_conn:
            sqlite_conn.close()
        if pg_conn:
            pg_conn.close()

if __name__ == "__main__":
    if migrate():
        print("\n🚀 Ready for production!")
    else:
        sys.exit(1)
