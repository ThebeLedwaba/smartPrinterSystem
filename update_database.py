# update_database.py - COMPLETE DATABASE SETUP
import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_FILE = "printers.db"

def init_database():
    """Initialize or update the database with all tables and columns"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        print("Starting database initialization...")
        
        # Users table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )''')
        print("✓ Users table created/verified")

        # Printers table
        cursor.execute('''CREATE TABLE IF NOT EXISTS printers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )''')
        print("✓ Printers table created/verified")

        # Printer states table
        cursor.execute('''CREATE TABLE IF NOT EXISTS printer_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time REAL,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )''')
        print("✓ Printer states table created/verified")

        # Alerts table
        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT NOT NULL,
            type TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'medium',
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT FALSE,
            acknowledged_by TEXT,
            acknowledged_at TIMESTAMP,
            resolved BOOLEAN DEFAULT FALSE,
            resolved_at TIMESTAMP,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )''')
        print("✓ Alerts table created/verified")

        # Print jobs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS print_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            printer_ip TEXT NOT NULL,
            username TEXT NOT NULL,
            document_name TEXT NOT NULL,
            pages INTEGER NOT NULL,
            color_pages INTEGER DEFAULT 0,
            duplex_pages INTEGER DEFAULT 0,
            job_size INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            cost REAL DEFAULT 0,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )''')
        print("✓ Print jobs table created/verified")

        # Printer details table
        cursor.execute('''CREATE TABLE IF NOT EXISTS printer_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT UNIQUE NOT NULL,
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
            color_cost_per_page REAL DEFAULT 0.15,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )''')
        print("✓ Printer details table created/verified")

        # Maintenance logs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT NOT NULL,
            maintenance_type TEXT NOT NULL,
            description TEXT,
            technician TEXT,
            cost REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            next_maintenance TEXT,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )''')
        print("✓ Maintenance logs table created/verified")

        # Add default users if they don't exist
        admin_password = generate_password_hash("admin123")
        tech_password = generate_password_hash("tech123")
        user_password = generate_password_hash("user123")
        
        cursor.execute('''INSERT OR IGNORE INTO users (username, password_hash, role) 
                          VALUES (?, ?, ?)''', ('admin', admin_password, 'admin'))
        cursor.execute('''INSERT OR IGNORE INTO users (username, password_hash, role) 
                          VALUES (?, ?, ?)''', ('technician', tech_password, 'technician'))
        cursor.execute('''INSERT OR IGNORE INTO users (username, password_hash, role) 
                          VALUES (?, ?, ?)''', ('user1', user_password, 'user'))
        print("✓ Default users created")

        # Now update any existing tables with new columns
        update_existing_tables(cursor)
        
        conn.commit()
        print("\n🎉 Database initialization completed successfully!")
        print("Default login credentials:")
        print("  - Admin: admin / admin123")
        print("  - Technician: technician / tech123") 
        print("  - User: user1 / user123")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        conn.rollback()
    finally:
        conn.close()

def update_existing_tables(cursor):
    """Update existing tables with new columns if they don't exist"""
    print("\nChecking for schema updates...")
    
    # Update users table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        print("✓ Added last_login to users table")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
        print("✓ Added is_active to users table")
    except sqlite3.OperationalError:
        pass
    
    # Update printers table
    printer_columns = [
        ('department', 'TEXT'),
        ('model', 'TEXT'),
        ('serial_number', 'TEXT'),
        ('purchase_date', 'TEXT'),
        ('warranty_expiry', 'TEXT'),
        ('is_active', 'BOOLEAN DEFAULT TRUE')
    ]
    
    for column_name, column_type in printer_columns:
        try:
            cursor.execute(f"ALTER TABLE printers ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added {column_name} to printers table")
        except sqlite3.OperationalError:
            pass
    
    # Update alerts table
    alert_columns = [
        ('severity', 'TEXT NOT NULL DEFAULT "medium"'),
        ('resolved', 'BOOLEAN DEFAULT FALSE'),
        ('resolved_at', 'TIMESTAMP')
    ]
    
    for column_name, column_type in alert_columns:
        try:
            cursor.execute(f"ALTER TABLE alerts ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added {column_name} to alerts table")
        except sqlite3.OperationalError:
            pass
    
    # Update print_jobs table
    job_columns = [
        ('color_pages', 'INTEGER DEFAULT 0'),
        ('duplex_pages', 'INTEGER DEFAULT 0'),
        ('job_size', 'INTEGER DEFAULT 0'),
        ('completed_at', 'TIMESTAMP'),
        ('cost', 'REAL DEFAULT 0')
    ]
    
    for column_name, column_type in job_columns:
        try:
            cursor.execute(f"ALTER TABLE print_jobs ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added {column_name} to print_jobs table")
        except sqlite3.OperationalError:
            pass
    
    # Update printer_details table
    detail_columns = [
        ('next_maintenance', 'TEXT'),
        ('cost_per_page', 'REAL DEFAULT 0.05'),
        ('color_cost_per_page', 'REAL DEFAULT 0.15')
    ]
    
    for column_name, column_type in detail_columns:
        try:
            cursor.execute(f"ALTER TABLE printer_details ADD COLUMN {column_name} {column_type}")
            print(f"✓ Added {column_name} to printer_details table")
        except sqlite3.OperationalError:
            pass

def check_database_status():
    """Check the current database status"""
    if not os.path.exists(DATABASE_FILE):
        print("❌ Database file does not exist")
        return False
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists and has required columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist")
            return False
        
        # Check for last_login column
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_login' not in columns:
            print("❌ last_login column missing from users table")
            return False
        
        print("✅ Database is properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("Smart Printer System - Database Setup")
    print("=" * 40)
    
    if os.path.exists(DATABASE_FILE):
        print(f"Found existing database: {DATABASE_FILE}")
        choice = input("Do you want to (1) Update existing database or (2) Delete and recreate? [1/2]: ")
        
        if choice == '2':
            os.remove(DATABASE_FILE)
            print("🗑️ Old database deleted")
            init_database()
        else:
            init_database()
    else:
        print("No existing database found. Creating new one...")
        init_database()
    
    # Verify the database
    print("\n" + "=" * 40)
    print("Verifying database setup...")
    check_database_status()