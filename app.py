import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize database
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "abc") 
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Set preferred URL scheme to http for Replit environment
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///learning_platform.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with app
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

with app.app_context():
    # Import models and routes
    import models  # noqa: F401
    import routes  # noqa: F401

    # Create all database tables
    db.create_all()

    # Add admin user if not exists
    from models import User
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True,
            xp=1000,
            level=10
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created")
    dummy_user = User.query.filter_by(username='dummy').first()
    if not dummy_user:
        dummy_user = User(
            username='dummy',
            email='dummy@example.com',
            password_hash=generate_password_hash('password123'),
            is_admin=False,
            xp=0,
            level=1
        )
        db.session.add(dummy_user)
        db.session.commit()
        logging.info("Dummy user created")
    from models import Course, Lesson

    # Add sample courses if not exists
    if Course.query.count() == 0:
        course1 = Course(
            title='Python Basics',
            description='Learn the basics of Python programming.',
            difficulty='Beginner',
            image_url='https://via.placeholder.com/300x200.png?text=Python+Basics'
        )
        course2 = Course(
            title='Flask for Beginners',
            description='Build web apps using Flask.',
            difficulty='Intermediate',
            image_url='https://via.placeholder.com/300x200.png?text=Flask+for+Beginners'
        )

        db.session.add_all([course1, course2])
        db.session.commit()

        # Add some lessons
        lesson1 = Lesson(
            course_id=course1.id,
            title='Introduction to Python',
            content='Python is a high-level, interpreted language...',
            order=1
        )
        lesson2 = Lesson(
            course_id=course2.id,
            title='Setting up Flask',
            content='Flask is a lightweight WSGI web application framework...',
            order=1
        )
        db.session.add_all([lesson1, lesson2])
        db.session.commit()
        logging.info("Sample courses and lessons created")


# User loader callback for Flask-Login
from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
from flask_login import login_user, current_user

@app.before_request
def auto_login():
    if not current_user.is_authenticated:
        dummy_user = User.query.filter_by(username='dummy').first()
        if dummy_user:
            login_user(dummy_user)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
