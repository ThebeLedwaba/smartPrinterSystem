#!/usr/bin/env python3
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def test_postgres():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Test counts from each table
        tables = ['users', 'printers', 'printer_states', 'alerts', 'audit_logs']
        
        print("📊 PostgreSQL Data Summary:")
        print("-" * 40)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            print(f"{table:20} | {result['count']:4} records")
        
        # Test a specific query
        cursor.execute("""
            SELECT p.name, p.ip, ps.status, ps.last_checked 
            FROM printers p 
            LEFT JOIN printer_states ps ON p.ip = ps.printer_ip 
            ORDER BY ps.last_checked DESC 
            LIMIT 3
        """)
        recent_printers = cursor.fetchall()
        
        print("\n🖨️  Recent Printer Status:")
        for printer in recent_printers:
            print(f"  - {printer['name']} ({printer['ip']}): {printer['status']}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_postgres():
        print("\n✅ PostgreSQL connection successful!")
    else:
        print("\n❌ PostgreSQL connection failed!")