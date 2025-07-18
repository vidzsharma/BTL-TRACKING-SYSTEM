from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from backend.db import init_db
from backend.routes import app as routes_app

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app, origins=Config.CORS_ORIGINS)
    jwt = JWTManager(app)
    
    # Initialize database
    init_db()
    
    # Register routes
    app.register_blueprint(routes_app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000) 