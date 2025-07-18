# HSBC BTL (Below the Line) Tracking Tool

A comprehensive tracking and management system for HSBC Bank's credit card sales team, designed to monitor user progress, manage leads, and upload/manage MIS (Management Information System) data with real-time analytics and role-based access control.

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Streamlit)   │◄──►│   (Flask API)   │◄──►│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Flask (Python REST API)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Data Processing**: Pandas, OpenPyXL
- **Visualization**: Plotly, Streamlit Charts

## 🚀 Features

### Core Features
- **User Authentication & Authorization**
  - Role-based access control (Admin, Team Leader, User)
  - JWT token-based authentication
  - Automatic login/logout tracking with location data

- **MIS Data Management**
  - Upload CSV/Excel files containing campaign data
  - Data validation and error handling
  - Real-time data processing and storage
  - Campaign and bank-wise analytics

- **Lead Progress Tracking**
  - Create and manage leads with campaign tags
  - Update lead status (new, in-progress, closed, rejected)
  - Progress history tracking
  - Performance analytics

- **Team Management**
  - Hierarchical user management
  - Team leader oversight of team members
  - Performance metrics and reporting

- **Analytics & Reporting**
  - Real-time dashboard with key metrics
  - Interactive charts and visualizations
  - Export functionality for reports
  - Performance tracking over time

### Role-Based Access

#### Admin
- Full system access
- User management
- All MIS data access
- System-wide reports
- Team performance monitoring

#### Team Leader
- Team member management
- Team-specific MIS data
- Team performance tracking
- Lead assignment and monitoring

#### User
- Personal lead management
- Own progress tracking
- Limited MIS data access
- Personal performance metrics

## 📋 Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed
2. **PostgreSQL** database server running
3. **Git** for version control

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd btl-tracking
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Using Docker (Recommended)
```bash
# Start PostgreSQL container
docker run --name hsbc-btl-db \
  -e POSTGRES_DB=hsbc_btl_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:13
```

#### Option B: Local PostgreSQL Installation
1. Install PostgreSQL on your system
2. Create database: `hsbc_btl_db`
3. Create user with appropriate permissions

### 5. Environment Configuration

Create a `.env` file in the root directory:
```env
# Database Configuration
DB_NAME=hsbc_btl_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
SECRET_KEY=your-super-secret-flask-key-change-in-production

# Development Configuration
DEBUG=True

# Optional: Google Maps API Key for location tracking
LOCATION_API_KEY=your-google-maps-api-key
```

### 6. Initialize Database
The database tables will be automatically created when you first run the application.

## 🚀 Running the Application

### Method 1: Single Command (Recommended)
```bash
streamlit run app.py
```

This will:
- Start the Flask backend server automatically
- Launch the Streamlit frontend
- Open the application in your default browser

### Method 2: Separate Backend and Frontend
```bash
# Terminal 1: Start Backend
python -m flask run --app=backend.routes --host=0.0.0.0 --port=5000

# Terminal 2: Start Frontend
streamlit run app.py
```

### Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000

## 👤 Default Login Credentials

### Admin User
- **Username**: `admin`
- **Password**: `admin123`

### Demo Users (Create via Admin Panel)
- **Team Leader**: `teamleader1` / `password123`
- **User**: `user1` / `password123`

## 📁 Project Structure

```
btl-tracking/
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── backend/                    # Backend API code
│   ├── __init__.py
│   ├── db.py                   # Database connection and setup
│   ├── auth.py                 # Authentication and authorization
│   ├── mis.py                  # MIS file processing
│   ├── progress.py             # Lead progress tracking
│   └── routes.py               # Flask API routes
│
├── frontend/                   # Frontend Streamlit code
│   ├── __init__.py
│   ├── helpers.py              # Helper functions
│   ├── login.py                # Login page
│   ├── dashboard.py            # Main dashboard
│   └── upload_mis.py           # MIS upload interface
│
├── data/                       # Data storage
│   ├── mis_uploads/            # Uploaded MIS files
│   └── PPIPL HSBC MIS.xlsx     # Sample MIS file
│
└── migrations/                 # Database migrations (future)
    └── 001_create_tables.sql
```

## 📊 MIS File Format

The system expects MIS files in the following format:

### Required Columns
- `bank` - Bank name
- `username` - User identifier
- `team_leader_name` - Team leader name
- `email_id` - Email address
- `campaign_tag` - Campaign identifier

### Supported Formats
- **CSV** (.csv)
- **Excel** (.xlsx, .xls)

### Sample Data
```csv
bank,username,team_leader_name,email_id,campaign_tag
HSBC,user1,leader1,user1@hsbc.com,CAMP001
HSBC,user2,leader1,user2@hsbc.com,CAMP001
```

## 🔧 Configuration

### Database Configuration
Edit `config.py` or set environment variables:
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/hsbc_btl_db"
```

### JWT Configuration
```python
JWT_SECRET_KEY = "your-secret-key"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
```

### File Upload Configuration
```python
UPLOAD_FOLDER = "data/mis_uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
```

## 📈 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/profile` - Get user profile

### MIS Management
- `POST /api/mis/upload` - Upload MIS file
- `GET /api/mis/data` - Get MIS data
- `GET /api/mis/statistics` - Get MIS statistics
- `GET /api/mis/campaign/<tag>` - Get campaign data

### Lead Management
- `GET /api/leads` - Get leads
- `POST /api/leads` - Create new lead
- `GET /api/leads/<id>` - Get lead details
- `PUT /api/leads/<id>/progress` - Update lead progress

### Progress Tracking
- `GET /api/progress/statistics` - Get progress statistics
- `GET /api/progress/campaign/<tag>` - Get campaign progress
- `GET /api/progress/performance` - Get performance data

### Team Management
- `GET /api/team/members` - Get team members

## 🔒 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control
- Session management
- Password hashing with bcrypt

### Data Security
- Input validation and sanitization
- SQL injection prevention
- File upload validation
- CORS configuration

### Location Tracking
- IP address logging
- User agent tracking
- Geolocation data (optional)
- Login/logout timestamps

## 🚀 Deployment

### Production Deployment

#### 1. Environment Setup
```bash
# Set production environment variables
export FLASK_ENV=production
export DEBUG=False
export DATABASE_URL=your-production-db-url
```

#### 2. Database Migration
```bash
# Run database migrations
python -c "from backend.db import init_database; init_database()"
```

#### 3. Start Services
```bash
# Start backend with production server
gunicorn -w 4 -b 0.0.0.0:5000 backend.routes:app

# Start frontend
streamlit run app.py --server.port 8501
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000 8501

CMD ["streamlit", "run", "app.py"]
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=backend --cov=frontend
```

### API Testing
```bash
# Test API endpoints
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📝 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: Connection to database failed
```
**Solution**: Check database credentials and ensure PostgreSQL is running.

#### 2. Backend Server Not Starting
```
Error: Backend server is not running
```
**Solution**: Check if port 5000 is available and Flask dependencies are installed.

#### 3. File Upload Errors
```
Error: File type not allowed
```
**Solution**: Ensure file is CSV or Excel format and under 16MB.

#### 4. Authentication Issues
```
Error: Invalid credentials
```
**Solution**: Use default admin credentials or check user database.

### Logs and Debugging
```bash
# Enable debug mode
export DEBUG=True

# Check application logs
tail -f logs/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary software for HSBC Bank. All rights reserved.

## 📞 Support

For technical support or questions:
- Email: support@hsbc.com
- Internal: Contact the development team

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Core BTL tracking functionality
- MIS upload and management
- Role-based access control
- Real-time analytics dashboard

### Planned Features
- Mobile app integration
- Advanced reporting
- Email notifications
- API rate limiting
- Multi-language support

---

**HSBC Bank - Below the Line Tracking Tool v1.0**
*Built with ❤️ for efficient sales team management* 