# Smart Printer System 🖨️ (Enterprise Edition)

A **production-ready, enterprise-grade printer monitoring and analytics platform** designed for IT departments and managed service providers. The system delivers real-time visibility, predictive maintenance insights, automated alerts, and secure role-based access across large printer fleets.

---

## 🚀 Key Features

### 🖥 Real-Time Monitoring

* Live printer status tracking (**Online / Offline**)
* Supply level monitoring (**Toner / Paper**) via **SNMP**
* Network reachability checks using **ICMP Ping**

### 📊 Analytics & Reporting

* **Executive Dashboard** – Infrastructure health, usage trends, and cost insights
* **Predictive Analytics** – Proactive maintenance and low-supply warnings
* **Automated Reports** – Generate **PDF** and **CSV** reports for technical and management teams

### 🔐 Security & Governance

* **Role-Based Access Control (RBAC)** – Admin, Technician, and Auditor roles
* **Audit Logging** – Full traceability of system access and actions
* **Rate Limiting & CSRF Protection** – Hardened against common attack vectors

### 🔔 Automation

* **Email Alerts** – Critical faults, low supplies, and maintenance reminders
* **Background Scheduling** – Continuous monitoring using APScheduler

---

## 🛠️ Technology Stack

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

## 📋 Prerequisites

* Python **3.8+**
* PostgreSQL database
* Network access to printers (SNMP & ICMP enabled)

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ThebeLedwaba/smartPrinterSystem.git
cd smartPrinterSystem
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Configuration

Create a `.env.production` file in the project root.

```ini
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/printers

# Enterprise Settings
ENTERPRISE_NAME="Acme Corp"
CURRENCY="R"

# Security
FLASK_SECRET=your_super_secret_key_here
ADMIN_PASSWORD=admin123
TECH_PASSWORD=tech123
AUDITOR_PASSWORD=auditor123

# Email Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_SENDER=notifications@example.com
EMAIL_PASSWORD=your_app_password

# SNMP
SNMP_COMMUNITY=public
```

> ⚠️ **Security Note:** Change all default passwords before deploying to production.

Ensure the PostgreSQL database exists:

```sql
CREATE DATABASE printers;
```

---

## 🏃‍♂️ Running the Application

The `dashboard.py` script initializes the database schema, starts background monitoring jobs, and launches the web server.

```bash
python dashboard.py
```

### Access

* **Dashboard:** [http://localhost:5000](http://localhost:5000)

### Default Roles

| Role       | Username   |
| ---------- | ---------- |
| Admin      | admin      |
| Technician | technician |
| Auditor    | auditor    |

Passwords are loaded from the `.env.production` file.

---

## 🗄 Database Management

* Tables are **auto-created on first run**
* `monitor.py` can be deployed independently as a **dedicated monitoring node**, sharing the same `DATABASE_URL`

---

## 🛡️ Security Features

* CSRF protection on all forms
* Secure password hashing (Werkzeug)
* Input validation & sanitization
* Rate limiting to mitigate brute-force attacks

---

## 📁 Project Structure

```
smartPrinterSystem/
├── dashboard.py      # Main Flask app & business logic
├── monitor.py        # Background printer monitoring service
├── templates/        # Jinja2 HTML templates
├── requirements.txt  # Python dependencies
└── .env.production   # Environment configuration
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

**Author:** Thebe Ledwaba
