# System Architecture

## Overview
The Smart Printer System (Enterprise Edition) is designed as a distributed, modular application that separates the user interface/business logic from the low-level device monitoring. It employs a traditional client-server architecture backed by a relational database, with an asynchronous background service for device polling.

## High-Level Architecture Diagram
```mermaid
graph TD
    User[User / Admin] -->|HTTPS| WebApp[Flask Web Dashboard]
    
    subgraph "Application Server"
        WebApp -->|Read/Write| DB[(PostgreSQL Database)]
        WebApp -->|Trigger| Anal[Analytics Engine]
        
        Monitor[Monitoring Service] -->|Poll (SNMP/Ping)| Printers[Network Printers]
        Monitor -->|Update Status| DB
        Monitor -->|Send Alerts| SMTP[SMTP / Email Server]
    end
    
    Anal -->|Read History| DB
    Anal -->|Generate Insights| WebApp
```

## Core Components

### 1. Web Application (`dashboard.py`)
*   **Framework**: Flask (Python)
*   **Role**: Serves the UI, handles user authentication, and provides reporting/management capabilities.
*   **Key Modules**:
    *   **Auth Manager**: Handles RBAC (Admin, Technician, Auditor) using `Flask-Login`.
    *   **Report Generator**: Uses `ReportLab` and `CSV` modules to generate downloadable compliance reports.
    *   **Visualizer**: Generates charts using `Matplotlib` (headless mode) for executive summaries.
    *   **Analytics Engine**: Analyzes historical data to predict supply depletion and maintenance events.

### 2. Monitoring Service (`monitor.py`)
*   **Execution**: Runs as a daemon/background thread or independent process.
*   **Role**: Continuously polls registered printers to ensure uptime and data accuracy.
*   **Protocols**:
    *   **SNMP (v1/v2c)**: Used to fetch granular details like toner levels, page counts, model info, and serial numbers.
    *   **ICMP (Ping)**: Used for rapid availability checks (Online/Offline status).
*   **Concurrency**: Uses `concurrent.futures.ThreadPoolExecutor` to poll multiple devices in parallel, ensuring scalability.

### 3. Database Layer (PostgreSQL)
*   **Role**: Central source of truth.
*   **Schema**:
    *   `users`: Stores credentials and role definitions.
    *   `printers`: Registry of managed devices (IP, Name, Location).
    *   `printer_states`: Live status buffer (reduces polling jitter).
    *   `printer_details`: Extended metadata (Supplies, Counters) stored partly as JSONB for flexibility.
    *   `alerts`: History of incidents and acknowledgments.
    *   `audit_logs`: Immutable record of all user actions for compliance.

## Data Flow

1.  **Polling Cycle**: 
    *   The `monitor` service wakes up (e.g., every 5 minutes).
    *   It fetches the list of active printers from the DB.
    *   It pings each printer; if online, it queries SNMP OIDs.
    *   Results are written to `printer_states` and `printer_details`.
    *   If a critical threshold is breached (e.g., Toner < 10%), a record is added to `alerts` and an email is dispatched.

2.  **User Interaction**:
    *   A user logs in. The app verifies credentials against `users` table.
    *   The Dashboard queries `printers` joined with `printer_states` to show live status.
    *   Executive reports trigger the `PredictiveAnalyticsEngine` to scan `print_jobs` history and calculate ROI/usage trends.

## Security Architecture

*   **Authentication**: Session-based auth with `werkzeug` password hashing.
*   **Authorization**: Decorator-based permission checks (`@admin_required`, `@technician_required`) ensure users only access appropriate features.
*   **Network Security**:
    *   SNMP requests are read-only (public community string).
    *   Database connection uses standard authentication.
    *   CSRF protection on all mutating web requests.
    *   Audit logging ensures accountability.
