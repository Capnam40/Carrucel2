import os
import logging
from flask_login import LoginManager

from app import app, db

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'  # type: ignore
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes import main_bp
from admin_routes import admin_bp

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Auto-initialize the application on startup
with app.app_context():
    from auto_setup import initialize_application
    initialize_application()

if __name__ == '__main__':
    # Start the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
