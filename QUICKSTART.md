# Quick Start Guide

Get the Smart Printer System up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ PostgreSQL database running
- ✅ Network access to your printers (SNMP enabled)

## Step 1: Clone and Navigate

```bash
git clone https://github.com/ThebeLedwaba/smartPrinterSystem.git
cd smartPrinterSystem
```

## Step 2: Install Dependencies

```bash
# Install Poetry (if not already installed)
pip install poetry

# Install project dependencies
poetry install
```

## Step 3: Configure Environment

```bash
# Copy the example configuration
cp .env.production.example .env.production

# Edit the configuration file
# At minimum, update these values:
# - DATABASE_URL
# - SECRET_KEY
# - SMTP settings (if you want email alerts)
# - User passwords
```

### Quick Configuration Example

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env.production with your values
DATABASE_URL=postgresql://user:password@localhost:5432/printer_db
SECRET_KEY=<generated-key-from-above>
```

## Step 4: Initialize Database

The database tables will be created automatically on first run, but you can verify the connection:

```bash
poetry run python test_postgres_connection.py
```

## Step 5: Add Your First Printer

Edit `printers.json` to add your printer:

```json
[
  {
    "ip": "192.168.1.100",
    "name": "Office Printer 1",
    "location": "Main Office"
  }
]
```

## Step 6: Start the Application

```bash
# Start the web dashboard
poetry run python dashboard.py
```

The dashboard will be available at: **http://localhost:5000**

## Step 7: Login

Use the default credentials (change these in `.env.production`):

- **Username:** `admin`
- **Password:** `admin` (or whatever you set in `.env.production`)

## Step 8: Start Monitoring (Optional)

In a separate terminal, start the monitoring service:

```bash
poetry run python monitor.py
```

This will continuously poll your printers and update their status.

---

## Next Steps

✅ **You're all set!** Here's what to do next:

1. **Add more printers** via the web dashboard
2. **Configure email alerts** in `.env.production`
3. **Set up monitoring intervals** to match your needs
4. **Review the security settings** and change default passwords
5. **Check out the full documentation** in [README.md](README.md)

## Troubleshooting Quick Fixes

### Database Connection Failed
```bash
# Verify PostgreSQL is running
# Check your DATABASE_URL in .env.production
# Ensure the database exists
```

### SNMP Not Working
```bash
# Verify SNMP is enabled on your printer
# Check the SNMP community string (default: public)
# Ensure firewall allows UDP port 161
```

### Can't Login
```bash
# Check your credentials in .env.production
# Ensure SECRET_KEY is set
# Clear browser cookies and try again
```

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Need help?** Check the [full documentation](README.md) or open an issue on GitHub.
