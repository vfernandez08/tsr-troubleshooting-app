import os
import logging
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure session for maximum persistence
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 7 days
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_MAX_AGE'] = 604800  # 7 days in seconds

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///tsr_troubleshooting.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models
    import routes

    # Create all database tables
    db.create_all()

# Template filters
@app.template_filter('datetime')
def datetime_filter(timestamp):
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return ''

@app.template_filter('duration')
def duration_filter(start_time, end_time=None):
    if not start_time:
        return ''

    end = end_time or datetime.now().timestamp()
    duration = int(end - start_time)

    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
