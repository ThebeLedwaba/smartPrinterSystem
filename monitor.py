# monitor.py - PostgreSQL Version with live status tracking
import time
import os
import logging
from ping3 import ping
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import concurrent.futures
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pysnmp.hlapi import *
import json
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# ------------------- Load environment -------------------
load_dotenv(".env.production")

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "admin@company.com")

SNMP_COMMUNITY = os.getenv("SNMP_COMMUNITY", "public")
SNMP_TIMEOUT = 3
SNMP_RETRIES = 1

POSTGRES_URL = os.getenv("DATABASE_URL")

# ------------------- Logging Setup ---------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("printer_monitor.log", encoding="utf-8")
    ]
)

# ------------------- PostgreSQL Connection -------------
def get_db_connection():
    if not POSTGRES_URL:
        raise RuntimeError("DATABASE_URL not set! Monitor requires PostgreSQL.")
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)

# ------------------- SNMP Helper ------------------------
def snmp_get(ip: str, oid: str) -> Optional[str]:
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(SNMP_COMMUNITY, mpModel=1),
            UdpTransportTarget((ip, 161), timeout=SNMP_TIMEOUT, retries=SNMP_RETRIES),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication or errorStatus:
            return None
        return str(varBinds[0][1])
    except Exception:
        return None

# ------------------- Professional Printer Monitor ------
class ProfessionalPrinterMonitor:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.snmp_oids = self._load_snmp_oids()
        self.printer_statuses = {}  # ip -> online/offline
        self.alerts = {}             # ip -> list of alerts
        self.check_db_connection()

    def check_db_connection(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            logging.info("PostgreSQL connection verified.")
        except Exception as e:
            logging.warning(f"Database not available. Monitor will run in NO-DB mode: {e}")

    def _load_snmp_oids(self):
        return {
            "hp": {
                "model": "1.3.6.1.2.1.25.3.2.1.3.1",
                "serial": "1.3.6.1.2.1.43.5.1.1.17.1",
                "uptime": "1.3.6.1.2.1.1.3.0",
                "supplies": {
                    "black_toner": "1.3.6.1.2.1.43.11.1.1.9.1.1"
                },
                "counters": {
                    "total_pages": "1.3.6.1.2.1.43.10.2.1.4.1.1"
                }
            },
            "generic": {
                "model": "1.3.6.1.2.1.1.1.0",
                "uptime": "1.3.6.1.2.1.1.3.0",
                "supplies": {
                    "black_toner": "1.3.6.1.2.1.43.11.1.1.9.1.1"
                },
                "counters": {
                    "total_pages": "1.3.6.1.2.1.43.10.2.1.4.1.1"
                }
            }
        }

    # ---------------- Printer Type Detection ----------------
    def detect_printer_type(self, printer_ip: str) -> str:
        sys_desc = snmp_get(printer_ip, "1.3.6.1.2.1.1.1.0")
        if not sys_desc:
            return "generic"
        sys_desc = sys_desc.lower()
        if "hp" in sys_desc or "hewlett" in sys_desc:
            return "hp"
        return "generic"

    # ---------------- Collect SNMP Details -----------------
    def get_printer_details_snmp(self, ip: str) -> Dict:
        ptype = self.detect_printer_type(ip)
        oids = self.snmp_oids.get(ptype, self.snmp_oids["generic"])
        details = {
            "model": snmp_get(ip, oids["model"]) or "Unknown",
            "serial_number": snmp_get(ip, oids.get("serial", "")) or "Unknown",
            "printer_type": ptype,
            "supplies": {},
            "counters": {},
            "status": {"uptime_hours": 0, "state": "unknown"},
            "firmware": snmp_get(ip, "1.3.6.1.2.1.43.5.1.1.1.2.1") or "Unknown"
        }
        for sname, soid in oids["supplies"].items():
            val = snmp_get(ip, soid)
            details["supplies"][sname] = int(val) if val and val.isdigit() else 100
        for cname, coid in oids["counters"].items():
            val = snmp_get(ip, coid)
            details["counters"][cname] = int(val) if val and val.isdigit() else 0
        uptime_raw = snmp_get(ip, oids.get("uptime", ""))
        if uptime_raw and uptime_raw.isdigit():
            details["status"]["uptime_hours"] = int(uptime_raw) // 360000
        return details

    # ---------------- Ping Printer ------------------------
    def ping_printer(self, printer_dict):
        """Ping a printer and return its status"""
        try:
            ip = printer_dict.get("ip")
            if not ip:
                return printer_dict, "unknown", None
                
            response = ping(ip, timeout=2)
            if response is not None:
                return printer_dict, "online", round(response * 1000, 2)
            return printer_dict, "offline", None
        except Exception as e:
            logging.warning(f"Ping error for {printer_dict.get('ip', 'unknown')}: {e}")
            return printer_dict, "offline", None

    # ---------------- Update Status & DB ------------------
    def update_printer_status(self, ip, name, status, supplies={}):
        self.printer_statuses[ip] = status
        self.alerts[ip] = self.check_alerts(ip, name, status, supplies)

        if not POSTGRES_URL:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Printer States table
            cursor.execute("""
                INSERT INTO printer_states (printer_ip, status, response_time, last_checked)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (printer_ip) DO UPDATE
                SET status = EXCLUDED.status,
                    response_time = EXCLUDED.response_time,
                    last_checked = EXCLUDED.last_checked
            """, (ip, status, None, datetime.now().isoformat()))

            # Printer Details table
            if status == "online":
                d = self.get_printer_details_snmp(ip)
                cursor.execute("""
                    INSERT INTO printer_details
                    (printer_ip, model, serial_number, supplies_json, counters_json, status_json, printer_type, firmware, last_updated)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (printer_ip) DO UPDATE
                    SET model = EXCLUDED.model,
                        serial_number = EXCLUDED.serial_number,
                        supplies_json = EXCLUDED.supplies_json,
                        counters_json = EXCLUDED.counters_json,
                        status_json = EXCLUDED.status_json,
                        printer_type = EXCLUDED.printer_type,
                        firmware = EXCLUDED.firmware,
                        last_updated = EXCLUDED.last_updated
                """, (
                    ip, d["model"], d["serial_number"],
                    json.dumps(d["supplies"]), json.dumps(d["counters"]),
                    json.dumps(d["status"]), d["printer_type"], d["firmware"],
                    datetime.now().isoformat()
                ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logging.warning(f"DB update failed for {ip}: {e}")

    # ---------------- Alert Checker ----------------------
    def check_alerts(self, ip, name, status, supplies: Dict):
        alerts = []
        if status == "offline":
            alerts.append({"type":"critical","printer_ip":ip,"message":f"Printer {name} is offline","timestamp":datetime.now().isoformat()})
        elif status == "online":
            blk = supplies.get("black_toner", 100)
            if blk < 10:
                alerts.append({"type":"critical","printer_ip":ip,"message":f"Very low black toner ({blk}%) on {name}","timestamp":datetime.now().isoformat()})
            elif blk < 20:
                alerts.append({"type":"warning","printer_ip":ip,"message":f"Low black toner ({blk}%) on {name}","timestamp":datetime.now().isoformat()})
        return alerts

    # ---------------- Email Alerts -----------------------
    def send_email_alert(self, subject, body):
        if not (EMAIL_SENDER and EMAIL_PASSWORD):
            return False
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = EMAIL_RECEIVER
            msg.attach(MIMEText(body, "plain"))
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            logging.info(f"Email alert sent: {subject}")
            return True
        except Exception as e:
            logging.warning(f"Failed to send email: {e}")
            return False

    # ---------------- Main Check Loop -------------------
    def check_printers(self):
        logging.info("Running printer monitor loop...")
        try:
            if not POSTGRES_URL:
                printers = [{"ip": "127.0.0.1", "name": "SimPrinter"}]  # fallback
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM printers WHERE is_active = TRUE")
                printers = cursor.fetchall()
                cursor.close()
                conn.close()

            if not printers:
                logging.warning("No active printers found in database")
                return

            # Convert printers to list of dictionaries
            printer_list = [dict(printer) for printer in printers]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all ping tasks
                future_to_printer = {}
                for printer_dict in printer_list:
                    future = executor.submit(self.ping_printer, printer_dict)
                    future_to_printer[future] = printer_dict
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_printer):
                    try:
                        printer_dict, status, response_time = future.result()
                        ip = printer_dict.get("ip")
                        name = printer_dict.get("name", ip)
                        
                        if ip:  # Only process if we have an IP
                            # Get supplies from database
                            supplies = {}
                            try:
                                if POSTGRES_URL:
                                    conn = get_db_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("SELECT supplies_json FROM printer_details WHERE printer_ip = %s", (ip,))
                                    row = cursor.fetchone()
                                    if row and row["supplies_json"]:
                                        supplies = json.loads(row["supplies_json"])
                                    cursor.close()
                                    conn.close()
                            except Exception as e:
                                logging.warning(f"Could not get supplies for {ip}: {e}")
                            
                            # Update status & alerts
                            self.update_printer_status(ip, name, status, supplies)
                            
                    except Exception as e:
                        logging.error(f"Error processing printer result: {e}")

            logging.info(f"Check completed for {len(printer_list)} printers.")
            
        except Exception as e:
            logging.warning(f"Error in check_printers: {e}")

    # ---------------- Start / Stop Monitoring -------------
    def start_monitoring(self):
        try:
            self.scheduler.add_job(
                self.check_printers,
                IntervalTrigger(minutes=5),
                id="printer_check",
                replace_existing=True,
                max_instances=1
            )
            self.scheduler.start()
            logging.info("Printer Monitor started.")
            self.check_printers()  # Run initial check
        except Exception as e:
            logging.warning(f"Failed to start monitoring: {e}")

    def stop_monitoring(self):
        self.scheduler.shutdown()
        logging.info("Monitor stopped.")

    # ---------------- Live Getters -----------------------
    def get_printer_status(self, ip):
        return self.printer_statuses.get(ip, "unknown")

    def get_alerts(self, ip):
        return self.alerts.get(ip, [])

# ---------------------- MAIN ---------------------------
if __name__ == "__main__":
    logging.info("Starting Professional Printer Monitor")
    monitor = ProfessionalPrinterMonitor()
    monitor.start_monitoring()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Stopping monitor...")
        monitor.stop_monitoring()