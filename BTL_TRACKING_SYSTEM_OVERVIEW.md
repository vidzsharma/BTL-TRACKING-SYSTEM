# HSBC BTL Tracking Tool - System Overview

## Executive Summary

The HSBC BTL (Below the Line) Tracking Tool is a comprehensive lead management and analytics platform designed to streamline HSBC's credit card sales operations. The system provides three-tier user management with role-based access control, real-time analytics, and comprehensive MIS data tracking for improved team performance and decision-making.

## System Purpose

### Primary Objectives
1. **Centralized Lead Management**: Track credit card leads from generation to conversion
2. **Performance Analytics**: Provide real-time insights into team and individual performance
3. **Compliance Tracking**: Monitor user activity with location and time tracking
4. **Data-Driven Decisions**: Comprehensive MIS analytics for strategic planning
5. **Team Management**: Hierarchical structure for effective oversight

### Target Users
- **Administrators**: System management and global oversight
- **Team Leaders**: Team performance monitoring and analytics
- **Direct Sales Agents (DSAs)**: Lead management and personal analytics

## System Architecture

### Technology Stack
```
Frontend:     Streamlit (Python web framework)
Backend:      Flask (Python web framework)
Database:     SQLite (Relational database)
Auth:         JWT (JSON Web Tokens)
Data Proc:    Pandas, OpenPyXL
Viz:          Plotly, Streamlit Charts
Location:     ip-api.com (Geolocation)
```

### Three-Tier Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │   Application   │    │     Data        │
│      Layer      │    │      Layer      │    │     Layer       │
│                 │    │                 │    │                 │
│   Streamlit     │◄──►│   Flask API     │◄──►│   SQLite DB     │
│   Frontend      │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Features

### 1. Authentication & Authorization
- **JWT-based Authentication**: Secure token-based sessions
- **Three-Tier Role System**: Admin > Team Leader > User
- **Role-based Access Control**: Data isolation by user role
- **Password Security**: Werkzeug hashing for secure storage

### 2. Lead Management
- **Lead Creation**: Create and assign leads to team members
- **Status Tracking**: Track lead progress (new, in-progress, closed, rejected)
- **Progress Notes**: Add remarks and updates to leads
- **Campaign Tracking**: Associate leads with specific campaigns

### 3. MIS Data Analytics
- **60+ Data Fields**: Comprehensive MIS data processing
- **Key Fields Include**:
  - FORM CAMPAIGN_ID
  - APPLICATION STATUS
  - CUSTOMER DROPPED PAGE
  - LEAD GENERATION STAGE
  - CARD TYPE
  - Status, Disposition, Called-Date, Remarks, Attempt, Booking-Status
- **Real-time Analytics**: Live dashboard updates
- **Role-based Filtering**: Appropriate data access per user role

### 4. User Activity Tracking
- **Login Monitoring**: Track user login timestamps
- **Location Tracking**: IP-based geolocation for accountability
- **Activity Patterns**: Analyze login frequency and patterns
- **Team Engagement**: Monitor team member activity levels

### 5. Team Performance Analytics
- **Individual Metrics**: Personal performance tracking
- **Team Comparison**: Compare team member performance
- **Success Rates**: Track conversion and success metrics
- **Trend Analysis**: Historical performance trends

## User Roles & Permissions

### Administrator
- **Access**: Full system access
- **Capabilities**:
  - User creation and management
  - Team structure configuration
  - Global analytics and reporting
  - System configuration
- **Data Access**: All users, all leads, all MIS data

### Team Leader
- **Access**: Team management and analytics
- **Capabilities**:
  - View team member performance
  - Access team MIS analytics
  - Monitor team login activity
  - Lead assignment and tracking
- **Data Access**: Assigned team members' data only

### User (DSA)
- **Access**: Personal lead management
- **Capabilities**:
  - Create and manage own leads
  - View personal analytics
  - Access own MIS data
  - Update lead progress
- **Data Access**: Own data only (filtered by FORM CAMPAIGN_ID)

## Data Flow

### MIS Data Processing
```
Excel File (data/) → Pandas Processing → Database Storage → Analytics Generation → Dashboard Display
```

### Lead Management
```
Lead Creation → Assignment → Status Updates → Progress Tracking → Performance Analytics
```

### User Activity
```
Login → IP Capture → Geolocation → Activity Logging → Analytics Dashboard
```

## Security Features

### Authentication Security
- JWT token-based authentication
- Secure password hashing
- Session timeout management
- Role-based authorization

### Data Security
- SQL injection prevention
- Input validation and sanitization
- Role-based data access control
- Audit trail logging

### Privacy Protection
- Location tracking with user consent
- Data isolation by role
- Secure API communication
- Error handling without data exposure

## Performance & Scalability

### Current Performance
- **Response Time**: < 3 seconds for dashboard loads
- **Concurrent Users**: Support for 100+ users
- **Data Volume**: Handle 10,000+ MIS records
- **Real-time Updates**: Live data refresh

### Scalability Features
- **Modular Architecture**: Easy component scaling
- **Database Optimization**: Indexed queries for performance
- **Caching Strategy**: Session and API response caching
- **Horizontal Scaling**: Ready for load balancer deployment

## System Components

### Frontend Modules
```
frontend/
├── login.py              # Authentication interface
├── dashboard.py          # Main dashboard with analytics
├── lead_management.py    # Lead CRUD operations
├── team_progress.py      # Team analytics and performance
├── team_management.py    # User and team management
├── reports.py           # Reporting and analytics
└── helpers.py           # Shared utilities and API calls
```

### Backend Modules
```
backend/
├── auth.py              # Authentication and authorization
├── db.py                # Database operations and schema
├── routes.py            # API endpoint definitions
├── progress.py          # Analytics and reporting logic
└── mis.py               # MIS data processing
```

### Database Schema
```sql
users                    # User accounts and roles
leads                    # Lead information and tracking
mis_data                 # MIS data with 60+ fields
login_logs               # User login activity
progress_tracking        # Lead progress history
```

## API Endpoints

### Core Endpoints
```
/api/login               # User authentication
/api/register            # User registration (Admin only)
/api/users               # User management
/api/leads               # Lead CRUD operations
/api/mis-files           # MIS data access
```

### Analytics Endpoints
```
/api/progress/statistics      # Performance statistics
/api/progress/mis-analytics   # MIS analytics
/api/progress/login-stats     # Login statistics
/api/progress/lead-analytics  # Lead analytics
/api/team/members             # Team member listing
/api/team/detailed-stats      # Detailed team statistics
```

## Business Value

### Operational Benefits
- **Improved Efficiency**: Centralized lead management
- **Better Visibility**: Real-time performance tracking
- **Enhanced Accountability**: User activity monitoring
- **Data-Driven Decisions**: Comprehensive analytics

### Performance Metrics
- **Lead Conversion**: Track and improve conversion rates
- **Team Productivity**: Monitor individual and team performance
- **User Engagement**: Track system adoption and usage
- **Data Accuracy**: Ensure data completeness and quality

### Compliance Benefits
- **Audit Trail**: Complete activity logging
- **Location Tracking**: Verify remote work compliance
- **Role-based Access**: Ensure data privacy
- **Activity Monitoring**: Track user engagement

## Future Enhancements

### Phase 2 Features
- Mobile application development
- Advanced BI integration
- Automated reporting
- Customer communication tools

### Phase 3 Features
- AI-powered lead scoring
- Predictive analytics
- CRM system integration
- Advanced workflow automation

## Technical Specifications

### System Requirements
- **Python**: 3.8 or higher
- **Database**: SQLite (development), PostgreSQL (production)
- **Web Server**: Streamlit (development), Nginx + Gunicorn (production)
- **Memory**: 2GB RAM minimum
- **Storage**: 10GB minimum for data storage

### Deployment Options
- **Development**: Local Python environment
- **Production**: Docker containers with load balancing
- **Cloud**: AWS/Azure deployment ready
- **On-premise**: Traditional server deployment

## Support & Maintenance

### Monitoring
- Health check endpoints
- Performance metrics collection
- Error logging and alerting
- User activity monitoring

### Maintenance
- Regular database backups
- Security updates and patches
- Performance optimization
- User training and support

This system overview provides a comprehensive understanding of the HSBC BTL Tracking Tool's capabilities, architecture, and business value, serving as a reference for stakeholders, developers, and users. 