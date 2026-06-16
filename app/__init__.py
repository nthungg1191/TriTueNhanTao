"""
Flask Application Factory
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy import inspect, text
from config.config import config
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name='development'):

    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Backfill attendance columns when the table already exists in an older schema.
    ensure_attendance_punch_columns(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'
    
    # Setup logging
    setup_logging(app)
    
    # Create necessary directories
    create_directories(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists(app.config['LOG_PATH']):
            os.makedirs(app.config['LOG_PATH'])
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_SIZE'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.info('Attendance System startup')


def create_directories(app):
    """Create necessary directories"""
    directories = [
        app.config['LOG_PATH'],
        app.config['BACKUP_PATH'],
        app.config['DATASET_PATH'],
        app.config['TRAIN_PATH'],
        app.config['UPLOAD_PATH'],
        app.config['FACE_ENCODINGS_PATH']
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app.logger.info(f'Created directory: {directory}')


def register_blueprints(app):
    """Register Flask blueprints"""
    # Import blueprints here to avoid circular imports
    from app.routes import auth, admin, kiosk, api, face_api, demo, notifications, employee, face_register
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(kiosk.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(face_api.face_api)
    app.register_blueprint(demo.bp)
    app.register_blueprint(notifications.bp)
    app.register_blueprint(employee.bp)
    app.register_blueprint(face_register.bp)


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def ensure_attendance_punch_columns(app):
    """Add missing punch columns to the attendance table for older databases."""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            if 'attendance' not in inspector.get_table_names():
                return

            existing_columns = {column['name'] for column in inspector.get_columns('attendance')}
            column_sql = {
                'check_in_time_2': 'DATETIME NULL',
                'check_out_time_2': 'DATETIME NULL',
                'check_in_photo_2': 'VARCHAR(255) NULL',
                'check_out_photo_2': 'VARCHAR(255) NULL',
            }

            with db.engine.begin() as connection:
                for column_name, ddl in column_sql.items():
                    if column_name not in existing_columns:
                        connection.execute(text(f'ALTER TABLE attendance ADD COLUMN {column_name} {ddl}'))
    except Exception as exc:
        app.logger.warning(f'Could not ensure attendance punch columns: {exc}')

