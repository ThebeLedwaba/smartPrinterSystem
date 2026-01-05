# migrate_to_sqlite.py
import sqlite3
import json
import os
from datetime import datetime

def migrate_data():
    """Migrate all JSON data to SQLite database"""
    
    # Check if database exists
    if not os.path.exists('printers.db'):
        print("❌ Database 'printers.db' not found!")
        print("💡 Run 'python create_database.py' first to create the database structure")
        return
    
    # Database connection
    conn = sqlite3.connect('printers.db')
    cursor = conn.cursor()
    
    print("Starting migration from JSON to SQLite...")
    
    migrated_count = 0
    
    # 1. Migrate printers
    if os.path.exists('printers.json'):
        with open('printers.json', 'r') as f:
            printers = json.load(f)
        
        for printer in printers:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO printers (name, ip, location)
                    VALUES (?, ?, ?)
                ''', (printer.get('name'), printer.get('ip'), printer.get('location', '')))
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating printer {printer.get('name')}: {e}")
        
        print(f"✅ Migrated {migrated_count} printers")
        migrated_count = 0
    else:
        print("❌ printers.json not found")
    
    # 2. Migrate printer states
    if os.path.exists('states.json'):
        with open('states.json', 'r') as f:
            states = json.load(f)
        
        for ip, status in states.items():
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO printer_states (printer_ip, status, last_checked)
                    VALUES (?, ?, ?)
                ''', (ip, status, datetime.now().isoformat()))
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating state for IP {ip}: {e}")
        
        print(f"✅ Migrated {migrated_count} printer states")
        migrated_count = 0
    else:
        print("❌ states.json not found")
    
    # 3. Migrate alerts
    if os.path.exists('alerts.json'):
        with open('alerts.json', 'r') as f:
            alerts = json.load(f)
        
        for alert in alerts:
            try:
                cursor.execute('''
                    INSERT INTO alerts (printer_ip, type, message, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    alert.get('printer_ip'),
                    alert.get('type', 'info'),
                    alert.get('message'),
                    alert.get('timestamp', datetime.now().isoformat())
                ))
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating alert: {e}")
        
        print(f"✅ Migrated {migrated_count} alerts")
        migrated_count = 0
    else:
        print("❌ alerts.json not found")
    
    # 4. Migrate print jobs
    if os.path.exists('print_jobs.json'):
        with open('print_jobs.json', 'r') as f:
            print_jobs = json.load(f)
        
        for job in print_jobs:
            try:
                cursor.execute('''
                    INSERT INTO print_jobs (job_id, printer_ip, username, document_name, pages, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.get('id'),
                    job.get('printer_ip'),
                    job.get('username'),
                    job.get('document_name'),
                    job.get('pages', 0),
                    job.get('status', 'completed'),
                    job.get('timestamp', datetime.now().isoformat())
                ))
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating print job: {e}")
        
        print(f"✅ Migrated {migrated_count} print jobs")
    else:
        print("❌ print_jobs.json not found")
    
    conn.commit()
    conn.close()
    print("🎉 Migration completed successfully!")
    print("📁 Your data is now in printers.db (SQLite database)")
    print("💡 You can safely delete the .json files after verifying the migration")

if __name__ == '__main__':
    migrate_data()