# Deployment Guide

Production deployment instructions for the Smart Printer System.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Production Environment Setup](#production-environment-setup)
- [Deployment Options](#deployment-options)
- [Security Hardening](#security-hardening)
- [Performance Tuning](#performance-tuning)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Backup & Recovery](#backup--recovery)

---

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] PostgreSQL database is set up and secured
- [ ] All environment variables are configured in `.env.production`
- [ ] Default passwords have been changed
- [ ] SECRET_KEY is a strong, random value
- [ ] SMTP/email settings are tested
- [ ] Firewall rules are configured
- [ ] SSL/TLS certificates are obtained (if using HTTPS)
- [ ] Backup strategy is in place
- [ ] Monitoring is configured

---

## Production Environment Setup

### 1. Server Requirements

**Minimum Specifications:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB SSD
- OS: Ubuntu 20.04+ / Windows Server 2019+ / RHEL 8+

**Recommended for 100+ printers:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv postgresql postgresql-contrib nginx
```

**RHEL/CentOS:**
```bash
sudo dnf install -y python3.10 python3-pip postgresql-server postgresql-contrib nginx
```

**Windows Server:**
- Install Python 3.10+ from python.org
- Install PostgreSQL from postgresql.org
- Install IIS or use Python's built-in server

### 3. PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE printer_monitor;
CREATE USER printer_admin WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE printer_monitor TO printer_admin;

# Exit psql
\q
```

**Configure PostgreSQL for remote access** (if needed):

Edit `/etc/postgresql/14/main/postgresql.conf`:
```conf
listen_addresses = 'localhost'  # Or specific IP
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```conf
# Allow local connections
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## Deployment Options

### Option 1: Systemd Service (Linux - Recommended)

#### Create Service Files

**1. Web Dashboard Service** (`/etc/systemd/system/printer-dashboard.service`):

```ini
[Unit]
Description=Smart Printer System Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/smartPrinterSystem
Environment="PATH=/opt/smartPrinterSystem/.venv/bin"
EnvironmentFile=/opt/smartPrinterSystem/.env.production
ExecStart=/opt/smartPrinterSystem/.venv/bin/python dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. Monitoring Service** (`/etc/systemd/system/printer-monitor.service`):

```ini
[Unit]
Description=Smart Printer System Monitor
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/smartPrinterSystem
Environment="PATH=/opt/smartPrinterSystem/.venv/bin"
EnvironmentFile=/opt/smartPrinterSystem/.env.production
ExecStart=/opt/smartPrinterSystem/.venv/bin/python monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Deploy Application

```bash
# Create deployment directory
sudo mkdir -p /opt/smartPrinterSystem
sudo chown www-data:www-data /opt/smartPrinterSystem

# Clone repository
cd /opt/smartPrinterSystem
sudo -u www-data git clone https://github.com/ThebeLedwaba/smartPrinterSystem.git .

# Install dependencies
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install poetry
sudo -u www-data .venv/bin/poetry install --no-dev

# Configure environment
sudo -u www-data cp .env.production.example .env.production
sudo -u www-data nano .env.production  # Edit configuration

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable printer-dashboard printer-monitor
sudo systemctl start printer-dashboard printer-monitor

# Check status
sudo systemctl status printer-dashboard
sudo systemctl status printer-monitor
```

### Option 2: Nginx Reverse Proxy (Recommended for Production)

**Install Nginx:**
```bash
sudo apt install nginx
```

**Configure Nginx** (`/etc/nginx/sites-available/printer-system`):

```nginx
upstream printer_dashboard {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name printer.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name printer.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/printer.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/printer.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/printer-system-access.log;
    error_log /var/log/nginx/printer-system-error.log;

    # Proxy settings
    location / {
        proxy_pass http://printer_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static {
        alias /opt/smartPrinterSystem/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/printer-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Windows Service

Use **NSSM** (Non-Sucking Service Manager):

```powershell
# Download NSSM
# Install dashboard service
nssm install PrinterDashboard "C:\Python310\python.exe" "C:\smartPrinterSystem\dashboard.py"
nssm set PrinterDashboard AppDirectory "C:\smartPrinterSystem"
nssm set PrinterDashboard Start SERVICE_AUTO_START

# Install monitor service
nssm install PrinterMonitor "C:\Python310\python.exe" "C:\smartPrinterSystem\monitor.py"
nssm set PrinterMonitor AppDirectory "C:\smartPrinterSystem"
nssm set PrinterMonitor Start SERVICE_AUTO_START

# Start services
nssm start PrinterDashboard
nssm start PrinterMonitor
```

---

## Security Hardening

### 1. Change Default Credentials

```bash
# In .env.production
ADMIN_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
TECHNICIAN_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
AUDITOR_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
```

### 2. Generate Strong SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Database Security

```sql
-- Revoke public access
REVOKE ALL ON DATABASE printer_monitor FROM PUBLIC;

-- Create read-only user for auditors
CREATE USER auditor_readonly WITH ENCRYPTED PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE printer_monitor TO auditor_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auditor_readonly;
```

### 4. Firewall Configuration

**Ubuntu (UFW):**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 192.168.1.0/24 to any port 5432  # PostgreSQL (local network only)
sudo ufw enable
```

**Windows:**
```powershell
# Allow HTTPS only
New-NetFirewallRule -DisplayName "Printer System HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

### 5. SSL/TLS Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d printer.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### 6. Rate Limiting

Already configured in the application. Adjust in `.env.production`:
```bash
RATE_LIMIT_PER_DAY=200
RATE_LIMIT_PER_HOUR=50
```

### 7. Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Default passwords changed
- [ ] Database access restricted to localhost
- [ ] Firewall configured
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Security headers set (via Nginx)
- [ ] Regular security updates scheduled

---

## Performance Tuning

### 1. Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_printer_states_timestamp ON printer_states(timestamp);
CREATE INDEX idx_printer_details_ip ON printer_details(ip);
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);

-- Configure PostgreSQL
-- Edit /etc/postgresql/14/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
```

### 2. Application Tuning

In `.env.production`:
```bash
# Reduce monitoring frequency for large fleets
MONITOR_INTERVAL=600  # 10 minutes

# Adjust worker pool
MAX_WORKERS=20  # Increase for more printers

# Enable caching
ENABLE_ANALYTICS=True
ANALYTICS_CACHE_DURATION=3600

# Database connection pool
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
```

### 3. System Resources

```bash
# Increase file descriptors (Linux)
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
```

---

## Monitoring & Maintenance

### 1. Log Rotation

Create `/etc/logrotate.d/printer-system`:
```conf
/opt/smartPrinterSystem/printer_monitor.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload printer-dashboard printer-monitor
    endscript
}
```

### 2. Health Checks

Create monitoring script (`/opt/smartPrinterSystem/healthcheck.sh`):
```bash
#!/bin/bash
# Check if services are running
systemctl is-active --quiet printer-dashboard || systemctl restart printer-dashboard
systemctl is-active --quiet printer-monitor || systemctl restart printer-monitor

# Check database connectivity
psql -U printer_admin -d printer_monitor -c "SELECT 1" > /dev/null 2>&1 || echo "Database down!"

# Check disk space
df -h | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $1 }' | while read output;
do
  usage=$(echo $output | awk '{ print $1}' | sed 's/%//g')
  partition=$(echo $output | awk '{ print $2 }')
  if [ $usage -ge 90 ]; then
    echo "Disk space critical: $partition at $usage%"
  fi
done
```

Add to crontab:
```bash
*/5 * * * * /opt/smartPrinterSystem/healthcheck.sh
```

### 3. Database Maintenance

Schedule weekly maintenance:
```bash
# Add to crontab
0 2 * * 0 psql -U printer_admin -d printer_monitor -c "VACUUM ANALYZE;"
```

---

## Backup & Recovery

### 1. Database Backup

**Automated daily backups:**
```bash
#!/bin/bash
# /opt/smartPrinterSystem/backup.sh
BACKUP_DIR="/var/backups/printer-system"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U printer_admin printer_monitor | gzip > $BACKUP_DIR/printer_monitor_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 1 * * * /opt/smartPrinterSystem/backup.sh
```

### 2. Configuration Backup

```bash
# Backup configuration
tar -czf /var/backups/printer-system/config_$(date +%Y%m%d).tar.gz \
  /opt/smartPrinterSystem/.env.production \
  /opt/smartPrinterSystem/printers.json
```

### 3. Recovery Procedure

```bash
# Restore database
gunzip < /var/backups/printer-system/printer_monitor_YYYYMMDD.sql.gz | \
  psql -U printer_admin printer_monitor

# Restore configuration
tar -xzf /var/backups/printer-system/config_YYYYMMDD.tar.gz -C /
```

---

## Post-Deployment Verification

### 1. Service Status
```bash
sudo systemctl status printer-dashboard
sudo systemctl status printer-monitor
```

### 2. Log Check
```bash
sudo journalctl -u printer-dashboard -f
sudo journalctl -u printer-monitor -f
```

### 3. Web Access
- Navigate to https://printer.yourdomain.com
- Login with admin credentials
- Verify dashboard loads correctly

### 4. Monitoring Test
- Add a test printer
- Wait for monitoring cycle
- Verify printer status updates

---

## Troubleshooting Deployment

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Quick checks:**
```bash
# Check service logs
sudo journalctl -u printer-dashboard -n 50
sudo journalctl -u printer-monitor -n 50

# Check database connection
psql -U printer_admin -d printer_monitor -c "SELECT version();"

# Check network connectivity
curl -I http://localhost:5000

# Check file permissions
ls -la /opt/smartPrinterSystem/
```

---

## Scaling Considerations

### For 500+ Printers:

1. **Separate monitoring nodes:**
   - Deploy multiple `monitor.py` instances
   - Each monitoring different printer segments
   - All writing to same database

2. **Database replication:**
   - Set up PostgreSQL read replicas
   - Use read replica for reports/analytics

3. **Load balancing:**
   - Multiple dashboard instances behind Nginx
   - Session persistence required

4. **Caching layer:**
   - Add Redis for session storage
   - Cache frequently accessed data

---

**Deployment complete!** Your Smart Printer System is now production-ready.
