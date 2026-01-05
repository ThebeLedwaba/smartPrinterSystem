# Smart Printer System (Enterprise Edition)

A comprehensive enterprise-grade solution for monitoring, managing, and analyzing network printers. This system provides real-time status updates, advanced reporting, predictive analytics, and secure role-based access control.

## 🚀 Key Features

*   **Real-Time Monitoring**: Live tracking of printer status (Online/Offline) and supply levels (Toner/Paper) via SNMP.
*   **Executive Dashboard**: High-level overview of infrastructure health, cost analytics, and ROI potential.
*   **Predictive Analytics**: Machine learning-inspired insights to predict maintenance needs and low supply warnings.
*   **Comprehensive Reporting**: Generate detailed PDF and CSV reports for management and technical teams.
*   **Role-Based Access Control (RBAC)**: secure access for Admins, Technicians, and Auditors.
*   **Automated Alerts**: Email notifications for critical errors, low supplies, and maintenance reminders.
*   **Audit Logging**: Full traceability of user actions for compliance and security.
*   **Database**: Robust PostgreSQL backend for scalability and data integrity.

## 🛠️ Technology Stack

*   **Backend**: Python, Flask
*   **Database**: PostgreSQL
*   **Monitoring**: SNMP (pysnmp), ICMP Ping
*   **Scheduling**: APScheduler
*   **Reporting**: ReportLab (PDF)
*   **Frontend**: HTML5, CSS3, Jinja2 Templates, JavaScript

## 📋 Prerequisites

*   Python 3.8 or higher
*   PostgreSQL Database
*   Network access to printers (for SNMP/Ping)

## ⚙️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/ThebeLedwaba/smartPrinterSystem.git
    cd smartPrinterSystem
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env.production` file in the root directory (or rename `.env` to `.env.production`).
    
    ```ini
    # Database Configuration
    DATABASE_URL=postgresql://user:password@localhost:5432/printers
    
    # Enterprice Config
    ENTERPRISE_NAME="Acme Corp"
    CURRENCY="R"
    
    # Security
    FLASK_SECRET=your_super_secret_key_here
    ADMIN_PASSWORD=admin123
    TECH_PASSWORD=tech123
    AUDITOR_PASSWORD=auditor123
    
    # Email Settings (for Alerts)
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    EMAIL_SENDER=notifications@example.com
    EMAIL_PASSWORD=your_app_password
    
    # SNMP
    SNMP_COMMUNITY=public
    ```
    > **Note:** Ensure you create a PostgreSQL database named `printers` (or match your DATABASE_URL).

## 🏃‍♂️ Usage

### Starting the Application
The `dashboard.py` script serves as the main entry point. It initializes the database schema, starts the background monitor, and launches the web server.

```bash
python dashboard.py
```

*   **Access the Dashboard**: Open [http://localhost:5000](http://localhost:5000) in your browser.
*   **Default Logins**:
    *   **Admin**: `admin` / (password from .env or `admin123`)
    *   **Technician**: `technician` / (password from .env or `tech123`)
    *   **Auditor**: `auditor` / (password from .env or `auditor123`)

### Database Administration
The system automatically creates necessary tables on first run. 
*   `monitor.py` can be run independently for a dedicated monitoring node, provided it shares the same `DATABASE_URL`.

## 🛡️ Security

*   **CSRF Protection**: Enabled on all forms.
*   **Password Hashing**: Uses Werkzeug security hashing.
*   **Sanitization**: Input validation to prevent injection attacks.
*   **Rate Limiting**: Protects against brute-force attacks.

## 📁 Project Structure

*   `dashboard.py`: Main Flask application and business logic.
*   `monitor.py`: Background service for printer polling.
*   `templates/`: HTML templates for the UI.
*   `requirements.txt`: Python package dependencies.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License.
