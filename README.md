# HSBC BTL Tracking Tool

## 📌 Executive Summary

The **HSBC BTL (Below the Line) Tracking Tool** is a comprehensive lead management and analytics platform designed to streamline credit card sales operations. It features three-tier user management, role-based access, real-time analytics, and MIS data tracking for performance evaluation and strategic planning.

---

## 🎯 System Purpose

### Primary Objectives
- Centralized lead tracking from generation to conversion
- Real-time team and individual performance analytics
- Compliance monitoring via location and activity tracking
- MIS-based decision support
- Hierarchical team management

### Target Users
- **Administrators**: Full system control and configuration
- **Team Leaders**: Team oversight and analytics
- **Direct Sales Agents (DSAs)**: Lead management and self-analysis

---

## 🏗️ System Architecture

### Technology Stack

```text
Frontend:     Streamlit
Backend:      Flask
Database:     SQLite
Auth:         JWT (JSON Web Tokens)
Data Proc:    Pandas, OpenPyXL
Viz:          Plotly, Streamlit Charts
Location:     ip-api.com
````

### Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │   Application   │    │     Data        │
│      Layer      │    │      Layer      │    │     Layer       │
│   Streamlit     │◄──►│   Flask API     │◄──►│   SQLite DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔑 Key Features

### 1. Authentication & Authorization

* JWT-based token auth
* Admin, Team Leader, and DSA roles
* Secure password hashing (Werkzeug)
* Session management and role-based access

### 2. Lead Management

* Lead creation, assignment, and tracking
* Status updates: new, in-progress, closed, rejected
* Campaign and remark tracking

### 3. MIS Analytics

* 60+ fields including campaign ID, application status, booking, attempts, etc.
* Real-time dashboard updates
* Role-based filtering and views

### 4. User Activity Tracking

* Login timestamps and geolocation (via IP)
* Activity heatmaps and trends

### 5. Team Performance

* Individual vs. team metrics
* Conversion and booking rates
* Performance trends and comparisons

---

## 🔐 Security Features

* JWT token authentication
* Secure password storage
* SQL injection prevention
* Role-based data filtering
* Geolocation tracking with consent
* Audit trail for all critical actions

---

## 👥 User Roles & Permissions

| Role            | Permissions                                                 |
| --------------- | ----------------------------------------------------------- |
| **Admin**       | Full control: users, teams, data, system config             |
| **Team Leader** | View and manage assigned team and leads                     |
| **User (DSA)**  | Manage own leads, track performance, view limited analytics |

---

## 🔁 Data Flow

### MIS Processing

```
Excel → Pandas → SQLite DB → Streamlit Dashboard
```

### Lead Management

```
Lead Creation → Assignment → Status Updates → Analytics
```

### User Activity

```
Login → IP Capture → Geo Logging → Dashboard Analytics
```

---

## 📂 Project Structure

### Frontend (`frontend/`)

* `login.py`: Auth UI
* `dashboard.py`: Analytics
* `lead_management.py`: Lead CRUD
* `team_progress.py`: Team metrics
* `team_management.py`: User/team setup
* `reports.py`: Reporting
* `helpers.py`: Utilities and shared functions

### Backend (`backend/`)

* `auth.py`: Login, JWT, registration
* `db.py`: Database models & queries
* `routes.py`: API routes
* `progress.py`: Stats and insights
* `mis.py`: MIS parsing and logic

### Database Tables

* `users`: Role & login info
* `leads`: Lead details
* `mis_data`: 60+ data points per record
* `login_logs`: Timestamp + IP
* `progress_tracking`: Lead history

---

## 📊 API Endpoints

### Core APIs

* `POST /api/login`
* `POST /api/register` (Admin only)
* `GET/POST /api/users`
* `GET/POST /api/leads`
* `GET /api/mis-files`

### Analytics APIs

* `/api/progress/statistics`
* `/api/progress/mis-analytics`
* `/api/progress/login-stats`
* `/api/progress/lead-analytics`
* `/api/team/members`
* `/api/team/detailed-stats`

---

## 🚀 Performance & Scalability

* < 3s response times for dashboards
* Supports 100+ concurrent users
* 10k+ MIS records in production
* Horizontal scaling and caching ready

---

## 🧩 Deployment & Requirements

### Requirements

* Python 3.8+
* SQLite (dev), PostgreSQL (prod)
* 2GB RAM, 10GB+ disk space

### Deployment

* Dev: Local with Streamlit
* Prod: Docker + Gunicorn + Nginx
* Cloud: AWS/Azure ready
* On-premise supported

---

## 📈 Business Value

* Boosts DSA and team productivity
* Improves lead conversion rates
* Enables real-time visibility and decision-making
* Ensures compliance and data privacy
* Complete audit trails and user accountability

---

## 📅 Future Enhancements

### Phase 2

* Mobile app version
* Automated reports
* BI tool integration
* Client communication tools

### Phase 3

* AI-based lead scoring
* Predictive analytics
* CRM integration
* Workflow automation

---

## 🛠️ Support & Maintenance

* Health check APIs
* Error & performance logs
* Scheduled database backups
* Regular updates and optimization

---

## 📞 Contact

For support or contributions, please contact the repository owner or submit an issue.

---
