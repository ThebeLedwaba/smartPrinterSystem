import json
import time
import os
import logging
from ping3 import ping
import smtplib
from email.mime.text import MIMEText
import concurrent.futures

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- Config ---
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.company.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "admin@company.com")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # seconds

PRINTERS_FILE = "printers.json"
STATES_FILE = "states.json"

def send_email(changes):
    """Send batch email notification for printer state changes."""
    if not changes:
        return
    subject = "Printer Status Alert"
    body_lines = [
        f"{printer['name']} ({printer['ip']}) is now {status.upper()}."
        for printer, status in changes
    ]
    body = "\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email sent: {subject} for {len(changes)} change(s)")
    except Exception as e:
        logging.warning(f"Failed to send email: {e}")

def load_json_file(filepath, default=None):
    """Load JSON file with error handling."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding {filepath}: {e}")
        return default if default is not None else {}

def validate_printer(printer):
    """Ensure printer dict has required fields."""
    return all(k in printer for k in ("name", "ip"))

def ping_printer(printer):
    if not validate_printer(printer):
        logging.warning(f"Invalid printer entry: {printer}")
        return printer, None
    try:
        response = ping(printer["ip"], timeout=2)
        status = "online" if response else "offline"
    except Exception as e:
        logging.warning(f"Ping error for {printer['name']} ({printer['ip']}): {e}")
        status = "offline"
    return printer, status

def check_printers():
    """Ping printers and detect status changes."""
    printers = load_json_file(PRINTERS_FILE, default=[])
    states = load_json_file(STATES_FILE, default={})

    changes = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(ping_printer, printers))

    for printer, status in results:
        if status is None:
            continue
        if states.get(printer["ip"]) != status:
            changes.append((printer, status))
            logging.info(f"{printer['name']} changed to {status.upper()}")
        states[printer["ip"]] = status

    if changes:
        send_email(changes)
    else:
        logging.info("No printer status changes detected.")

    try:
        with open(STATES_FILE, "w") as f:
            json.dump(states, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to write states file: {e}")

if __name__ == "__main__":
    logging.info("🖨️ Starting printer monitor...")
    while True:
        check_printers()
        time.sleep(CHECK_INTERVAL)
