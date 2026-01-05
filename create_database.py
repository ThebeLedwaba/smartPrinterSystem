# create_database.py
import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_tables():
    """Create the database tables structure"""
    
    # Remove existing database if it exists
    if os.path.exists('printers.db'):
        os.remove('printers.db')
        print("🗑️  Removed existing database")
    
    # Database connection
    conn = sqlite3.connect('printers.db')
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Users table with hashed passwords
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Printers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS printers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT UNIQUE NOT NULL,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Printer states table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS printer_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT NOT NULL,
            status TEXT NOT NULL,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )
    ''')
    
    # Alerts table with acknowledge feature
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_ip TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT FALSE,
            acknowledged_by TEXT,
            acknowledged_at TIMESTAMP,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )
    ''')
    
    # Print jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS print_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            printer_ip TEXT NOT NULL,
            username TEXT NOT NULL,
            document_name TEXT NOT NULL,
            pages INTEGER NOT NULL,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (printer_ip) REFERENCES printers (ip)
        )
    ''')
    
    # Create default admin user
    admin_password = "admin123"  # Change this in production!
    password_hash = generate_password_hash(admin_password)
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role) 
        VALUES (?, ?, ?)
    ''', ('admin', password_hash, 'admin'))
    
    conn.commit()
    conn.close()
    
    print("✅ Database tables created successfully!")
    print("👤 Default admin user created:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   ⚠️  Change this password in production!")

if __name__ == '__main__':
    create_tables()