import os
from datetime import timedelta

class Config:
    # Database Configuration - Using SQLite for easier setup
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///btl_tracking.db')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    

    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:8501', 'http://127.0.0.1:8501']
    
    # Location API Configuration
    LOCATION_API_URL = "http://ip-api.com/json/"
    
    # Pagination
    ITEMS_PER_PAGE = 20 