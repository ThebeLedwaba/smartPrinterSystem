# Smart Printer System (Enterprise Edition)

[![CI](https://github.com/ThebeLedwaba/smartPrinterSystem/actions/workflows/python-ci.yml/badge.svg)](https://github.com/ThebeLedwaba/smartPrinterSystem/actions/workflows/python-ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)

A **production-ready, enterprise-grade printer monitoring and analytics platform** designed for IT departments and managed service providers. The system delivers real-time visibility, predictive maintenance insights, automated alerts, and secure role-based access across large printer fleets.

## Quick Links

📚 **[Quick Start Guide](QUICKSTART.md)** • 🚀 **[Deployment Guide](DEPLOYMENT.md)** • 🔧 **[Troubleshooting](TROUBLESHOOTING.md)** • 📖 **[Architecture](architecture.md)** • 📝 **[Changelog](CHANGELOG.md)**



## Architecture Overview

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end
    
    subgraph "Application Server"
        WebApp[Flask Dashboard<br/>dashboard.py]
        Auth[Authentication<br/>& RBAC]
        Reports[Report Generator<br/>PDF/CSV]
        Analytics[Predictive Analytics<br/>Engine]
        
        WebApp --> Auth
        WebApp --> Reports
        WebApp --> Analytics
    end
    
    subgraph "Monitoring Layer"
        Monitor[Monitoring Service<br/>monitor.py]
        Scheduler[APScheduler<br/>Background Jobs]
        
        Monitor --> Scheduler
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        Cache[Status Cache]
        
        DB --> Cache
    end
    
    subgraph "External Systems"
        Printers[Network Printers<br/>SNMP/ICMP]
        SMTP[Email Server<br/>Alerts & Reports]
    end
    
    Browser -->|HTTPS| WebApp
    WebApp -->|Read/Write| DB
    Monitor -->|Poll Status| Printers
    Monitor -->|Update| DB
    Monitor -->|Send Alerts| SMTP
    Analytics -->|Query History| DB
    Reports -->|Send Reports| SMTP
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant Monitor as Monitoring Service
    participant DB as PostgreSQL
    participant Printer as Network Printer
    participant SMTP as Email Server
    participant Dashboard as Web Dashboard
    participant User as User/Admin
    
    Note over Monitor: Every 5 minutes
    Monitor->>DB: Fetch registered printers
    DB-->>Monitor: Printer list
    
    loop For each printer
        Monitor->>Printer: ICMP Ping
        Printer-->>Monitor: Online/Offline
        
        alt Printer Online
            Monitor->>Printer: SNMP Query (Toner, Paper, Counters)
            Printer-->>Monitor: Supply levels & status
            Monitor->>DB: Update printer_states & printer_details
            
            alt Critical threshold breached
                Monitor->>DB: Create alert record
                Monitor->>SMTP: Send email notification
            end
        end
    end
    
    User->>Dashboard: Login request
    Dashboard->>DB: Verify credentials
    DB-->>Dashboard: User role & permissions
    Dashboard-->>User: Dashboard view
    
    User->>Dashboard: Request report
    Dashboard->>DB: Query printer history
    DB-->>Dashboard: Historical data
    Dashboard->>Dashboard: Generate PDF/CSV
    Dashboard-->>User: Download report
```

### Component Interaction

```mermaid
graph LR
    subgraph "Core Components"
        A[dashboard.py<br/>3124 lines]
        B[monitor.py<br/>346 lines]
    end
    
    subgraph "Key Managers"
        C[NotificationManager<br/>Email Alerts]
        D[ReportGenerator<br/>PDF/CSV Export]
        E[PredictiveAnalytics<br/>Insights Engine]
        F[AuditLogger<br/>Compliance Tracking]
    end
    
    subgraph "Database Schema"
        G[users<br/>Authentication]
        H[printers<br/>Device Registry]
        I[printer_states<br/>Live Status]
        J[printer_details<br/>SNMP Data]
        K[alerts<br/>Notifications]
        L[audit_logs<br/>User Actions]
    end
    
    A --> C
    A --> D
    A --> E
    A --> F
    
    B --> C
    
    A --> G
    A --> H
    A --> I
    A --> J
    A --> K
    A --> L
    
    B --> H
    B --> I
    B --> J
    B --> K
```

---

## Key Features

### Real-Time Monitoring

* Live printer status tracking (Online / Offline)
* Supply level monitoring (Toner / Paper) via SNMP
* Network reachability checks using ICMP Ping

### Analytics & Reporting

* **Executive Dashboard** – Infrastructure health, usage trends, and cost insights
* **Predictive Analytics** – Proactive maintenance and low-supply warnings
* **Automated Reports** – Generate PDF and CSV reports for technical and management teams

### Security & Governance

* **Role-Based Access Control (RBAC)** – Admin, Technician, and Auditor roles
* **Audit Logging** – Full traceability of system access and actions
* **Rate Limiting & CSRF Protection** – Hardened against common attack vectors

### Automation

* **Email Alerts** – Critical faults, low supplies, and maintenance reminders
* **Background Scheduling** – Continuous monitoring using APScheduler

---

## Technology Stack

### Backend

* **Python 3.8+**
* **Flask** – Lightweight, scalable web framework
* **PostgreSQL** – Reliable, ACID-compliant relational database

### Monitoring & Automation

* **SNMP** (pysnmp) – Printer telemetry
* **ICMP Ping** – Network availability checks
* **APScheduler** – Scheduled monitoring jobs

### Reporting & UI

* **ReportLab** – Enterprise PDF reporting
* **HTML5 / CSS3 / JavaScript**
* **Jinja2 Templates** – Server-side rendered UI

---

## Prerequisites

* Python **3.8+**
* PostgreSQL database
* Network access to printers (SNMP & ICMP enabled)

---

## Installation & Running

### Option A: Local Development with Poetry

1.  **Install Poetry**:
    Follow instructions at [python-poetry.org](https://python-poetry.org/docs/#installation)

2.  **Install Dependencies**:
    ```bash
    poetry install
    ```

3.  **Setup Environment**:
    Create `.env.production` (see configuration section).

4.  **Run the Application**:
    ```bash
    poetry run python dashboard.py
    ```

### Option B: Manual Setup

1.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    ```

2.  **Install Dependencies**:
    ```bash
    pip install poetry
    poetry install --no-root
    ```

3.  **Run**:
    ```bash
    python dashboard.py
    ```

### Access

* **Dashboard:** [http://localhost:5000](http://localhost:5000)


| Role       | Username   |
| ---------- | ---------- |
| Admin      | admin      |
| Technician | technician |
| Auditor    | auditor    |

Passwords are loaded from the `.env.production` file.

---

## Configuration

### Environment Variables

Copy `.env.production.example` to `.env.production` and configure:

**Essential Settings:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/printer_monitor

# Security
SECRET_KEY=your-secret-key-here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Email Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
```

**Optional Settings:**
```bash
# Monitoring
MONITOR_INTERVAL=300  # 5 minutes
SNMP_TIMEOUT=5
MAX_WORKERS=10

# Alert Thresholds
TONER_LOW_THRESHOLD=10
PAPER_LOW_THRESHOLD=20

# Performance
ENABLE_ANALYTICS=True
ANALYTICS_CACHE_DURATION=3600
```

See [`.env.production.example`](.env.production.example) for all available options.

---

## Performance & Scalability

### System Requirements

| Deployment Size | Printers | CPU | RAM | Storage |
|----------------|----------|-----|-----|---------|
| Small | 1-50 | 2 cores | 4 GB | 20 GB |
| Medium | 51-200 | 4 cores | 8 GB | 50 GB |
| Large | 201-500 | 8 cores | 16 GB | 100 GB |
| Enterprise | 500+ | 16+ cores | 32+ GB | 200+ GB |

### Performance Metrics

- **Monitoring Interval**: 5 minutes (configurable)
- **Concurrent Printer Checks**: Up to 20 printers simultaneously
- **Database Queries**: Optimized with indexes, <100ms average response
- **Dashboard Load Time**: <2 seconds for 100 printers
- **Report Generation**: <10 seconds for 30-day reports

### Scalability Features

- **Horizontal Scaling**: Deploy multiple monitoring nodes
- **Database Replication**: PostgreSQL read replicas for analytics
- **Caching**: Analytics results cached for 1 hour
- **Connection Pooling**: Efficient database connection reuse

---

## Database Management

* Tables are **auto-created on first run**
* `monitor.py` can be deployed independently as a **dedicated monitoring node**, sharing the same `DATABASE_URL`
* **Data Retention**: Configurable (default: 90 days for printer_details)
* **Backup**: Automated daily backups recommended (see [DEPLOYMENT.md](DEPLOYMENT.md))

---

## Security Features

* **Authentication**: Session-based with secure password hashing
* **Authorization**: Role-based access control (RBAC)
* **CSRF Protection**: All forms protected against CSRF attacks
* **Input Validation**: Sanitization and validation on all inputs
* **Rate Limiting**: 200 requests/day, 50 requests/hour per IP
* **Audit Logging**: Complete trail of all user actions
* **Security Headers**: XSS protection, frame options, content type sniffing prevention

**Security Best Practices:**
- Change default passwords immediately
- Use strong SECRET_KEY (32+ characters)
- Enable HTTPS in production (see [DEPLOYMENT.md](DEPLOYMENT.md))
- Restrict database access to localhost
- Regular security updates



## Project Structure

```
smartPrinterSystem/
├── dashboard.py          # Main Flask app & business logic (3124 lines)
├── monitor.py            # Background printer monitoring service (346 lines)
├── templates/            # Jinja2 HTML templates
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Poetry configuration
├── architecture.md       # Detailed architecture documentation
├── .env.production.example  # Configuration template
├── QUICKSTART.md         # 5-minute setup guide
├── DEPLOYMENT.md         # Production deployment guide
├── TROUBLESHOOTING.md    # Common issues and solutions
└── CHANGELOG.md          # Version history
```

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add tests for new features
- Update documentation as needed
- Ensure CI/CD pipeline passes

See our documentation for more details:
- [Architecture Guide](architecture.md) - Understand the system design
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Debug common issues
- [Deployment Guide](DEPLOYMENT.md) - Production best practices

---

## Support & Community

- **Documentation**: Start with [QUICKSTART.md](QUICKSTART.md)
- **Issues**: [GitHub Issues](https://github.com/ThebeLedwaba/smartPrinterSystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ThebeLedwaba/smartPrinterSystem/discussions)

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Database powered by [PostgreSQL](https://www.postgresql.org/)
- SNMP monitoring via [PySNMP](https://github.com/pysnmp/pysnmp)
- PDF reports generated with [ReportLab](https://www.reportlab.com/)

---

**Author:** Thebe Ledwaba

**Version:** 1.0.0 | [Changelog](CHANGELOG.md)

