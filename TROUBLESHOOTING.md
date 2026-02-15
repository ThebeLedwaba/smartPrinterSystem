# Troubleshooting Guide

Common issues and solutions for the Smart Printer System.

## Table of Contents

- [Database Issues](#database-issues)
- [SNMP Connection Problems](#snmp-connection-problems)
- [Authentication & Login Issues](#authentication--login-issues)
- [Email/SMTP Issues](#emailsmtp-issues)
- [Monitoring Service Issues](#monitoring-service-issues)
- [Performance Issues](#performance-issues)
- [Network & Firewall](#network--firewall)
- [Debug Mode](#debug-mode)

---

## Database Issues

### Problem: "Could not connect to database"

**Symptoms:**
- Application fails to start
- Error message: `psycopg2.OperationalError`

**Solutions:**

1. **Verify PostgreSQL is running:**
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/Mac
   sudo systemctl status postgresql
   ```

2. **Check DATABASE_URL format:**
   ```bash
   # Correct format:
   DATABASE_URL=postgresql://username:password@host:port/database
   
   # Example:
   DATABASE_URL=postgresql://printer_admin:mypass123@localhost:5432/printer_monitor
   ```

3. **Test connection manually:**
   ```bash
   poetry run python test_postgres_connection.py
   ```

4. **Ensure database exists:**
   ```sql
   -- Connect to PostgreSQL and create database
   CREATE DATABASE printer_monitor;
   ```

### Problem: "Table does not exist"

**Solution:**
Tables are created automatically on first run. If they're missing:

```bash
# Run the database creation script
poetry run python create_database.py
```

### Problem: Database performance is slow

**Solutions:**

1. **Run database optimization:**
   ```bash
   poetry run python update_database.py
   ```

2. **Check database size:**
   ```sql
   SELECT pg_size_pretty(pg_database_size('printer_monitor'));
   ```

3. **Archive old data** (older than 90 days):
   ```sql
   DELETE FROM printer_details WHERE timestamp < NOW() - INTERVAL '90 days';
   VACUUM ANALYZE;
   ```

---

## SNMP Connection Problems

### Problem: "SNMP timeout" or "No response from printer"

**Symptoms:**
- Printers show as offline even though they're online
- Supply levels not updating

**Solutions:**

1. **Verify SNMP is enabled on the printer:**
   - Access printer web interface
   - Navigate to Network → SNMP settings
   - Enable SNMPv1 or SNMPv2c
   - Set community string (default: `public`)

2. **Test SNMP manually:**
   ```bash
   # Windows (install snmpwalk first)
   snmpwalk -v2c -c public 192.168.1.100 system
   
   # Linux/Mac
   snmpwalk -v2c -c public 192.168.1.100 system
   ```

3. **Check community string:**
   ```bash
   # In .env.production
   SNMP_COMMUNITY=public  # Must match printer setting
   ```

4. **Increase timeout:**
   ```bash
   # In .env.production
   SNMP_TIMEOUT=10  # Increase from default 5 seconds
   SNMP_RETRIES=5   # Increase from default 3
   ```

### Problem: "Wrong SNMP OIDs for my printer model"

**Solution:**

Different printer manufacturers use different OIDs. Check `monitor.py` for the OID mappings:

```python
# Common OIDs by manufacturer:
# HP: 1.3.6.1.2.1.43.11.1.1.9.1.1
# Canon: 1.3.6.1.2.1.43.11.1.1.9.1.1
# Brother: 1.3.6.1.4.1.2435.2.3.9.4.2.1.5.5.8.0
```

You can find your printer's OIDs using:
```bash
snmpwalk -v2c -c public <printer-ip> 1.3.6.1.2.1.43
```

---

## Authentication & Login Issues

### Problem: "Invalid username or password"

**Solutions:**

1. **Check credentials in `.env.production`:**
   ```bash
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-password-here
   ```

2. **Ensure SECRET_KEY is set:**
   ```bash
   # Generate new key if needed
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Clear browser cookies:**
   - Press `Ctrl+Shift+Delete`
   - Clear cookies for localhost:5000
   - Try logging in again

4. **Check for special characters:**
   - Avoid quotes in password
   - Use alphanumeric characters only

### Problem: "Session expired" too quickly

**Solution:**

Increase session timeout in `.env.production`:
```bash
SESSION_TIMEOUT=60  # Increase from default 30 minutes
```

### Problem: "CSRF token missing"

**Solution:**

Ensure CSRF protection is properly configured:
```bash
# In .env.production
CSRF_ENABLED=True
```

Clear browser cache and cookies, then try again.

---

## Email/SMTP Issues

### Problem: "Failed to send email alert"

**Solutions:**

1. **For Gmail users:**
   - Enable 2-factor authentication
   - Generate an App Password: https://myaccount.google.com/apppasswords
   - Use the app password in `.env.production`:
     ```bash
     SMTP_USERNAME=your-email@gmail.com
     SMTP_PASSWORD=your-16-char-app-password
     ```

2. **Check SMTP settings:**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587  # TLS
   # OR
   SMTP_PORT=465  # SSL
   ```

3. **Test SMTP connection:**
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-password')
   server.quit()
   ```

4. **Common SMTP servers:**
   ```bash
   # Gmail
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   
   # Outlook/Office365
   SMTP_SERVER=smtp.office365.com
   SMTP_PORT=587
   
   # Yahoo
   SMTP_SERVER=smtp.mail.yahoo.com
   SMTP_PORT=587
   ```

### Problem: Emails going to spam

**Solutions:**
- Add sender email to contacts
- Check SPF/DKIM records if using custom domain
- Use a professional email service (SendGrid, Mailgun, etc.)

---

## Monitoring Service Issues

### Problem: Monitor service crashes or stops

**Solutions:**

1. **Check logs:**
   ```bash
   tail -f printer_monitor.log
   ```

2. **Run in foreground for debugging:**
   ```bash
   poetry run python monitor.py
   ```

3. **Check for memory issues:**
   ```bash
   # Reduce concurrent workers
   MAX_WORKERS=5  # In .env.production
   ```

### Problem: Printers not being monitored

**Solutions:**

1. **Verify printers are registered:**
   - Check web dashboard → Printers list
   - Ensure printers are in database

2. **Check monitoring interval:**
   ```bash
   # In .env.production
   MONITOR_INTERVAL=300  # 5 minutes
   ```

3. **Manually trigger check:**
   ```python
   # In Python console
   from monitor import ProfessionalPrinterMonitor
   monitor = ProfessionalPrinterMonitor()
   monitor.check_printers()
   ```

---

## Performance Issues

### Problem: Dashboard is slow to load

**Solutions:**

1. **Enable analytics caching:**
   ```bash
   # In .env.production
   ENABLE_ANALYTICS=True
   ANALYTICS_CACHE_DURATION=3600  # 1 hour
   ```

2. **Optimize database:**
   ```bash
   poetry run python update_database.py
   ```

3. **Reduce data retention:**
   ```sql
   -- Keep only last 30 days
   DELETE FROM printer_details WHERE timestamp < NOW() - INTERVAL '30 days';
   ```

### Problem: High CPU usage

**Solutions:**

1. **Reduce monitoring frequency:**
   ```bash
   MONITOR_INTERVAL=600  # 10 minutes instead of 5
   ```

2. **Reduce concurrent workers:**
   ```bash
   MAX_WORKERS=5  # Reduce from default 10
   ```

---

## Network & Firewall

### Required Ports

Ensure these ports are open:

| Port | Protocol | Purpose |
|------|----------|---------|
| 5000 | TCP | Web Dashboard (HTTP) |
| 5432 | TCP | PostgreSQL Database |
| 161 | UDP | SNMP (Printer monitoring) |
| 587 | TCP | SMTP (Email alerts) |
| ICMP | - | Ping (Printer status) |

### Firewall Configuration

**Windows:**
```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Smart Printer System" -Direction Inbound -Program "C:\Path\To\python.exe" -Action Allow
```

**Linux (UFW):**
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 161/udp
```

---

## Debug Mode

### Enable Debug Logging

1. **In `.env.production`:**
   ```bash
   LOG_LEVEL=DEBUG
   FLASK_DEBUG=True  # Only for development!
   ```

2. **View detailed logs:**
   ```bash
   tail -f printer_monitor.log
   ```

3. **Check Flask logs:**
   ```bash
   poetry run python dashboard.py
   # Watch console output
   ```

### Common Debug Commands

```bash
# Test database connection
poetry run python test_postgres_connection.py

# Test SNMP connectivity
poetry run python test_monitor.py

# Check Python version
python --version

# Check installed packages
poetry show

# Verify environment variables
poetry run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

---

## Still Having Issues?

1. **Check the logs:**
   - `printer_monitor.log` - Monitoring service logs
   - Flask console output - Web application logs

2. **Enable debug mode** (see above)

3. **Search existing issues:** [GitHub Issues](https://github.com/ThebeLedwaba/smartPrinterSystem/issues)

4. **Open a new issue** with:
   - Error message (full traceback)
   - Your configuration (remove sensitive data)
   - Steps to reproduce
   - System information (OS, Python version, etc.)

---

**Pro Tip:** Most issues are related to configuration. Double-check your `.env.production` file!
