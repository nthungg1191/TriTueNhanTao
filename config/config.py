
import os
import pymysql
pymysql.install_as_MySQLdb()

from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

    if database_url:
        # Nếu lỡ nhập value có dấu nháy trong Railway thì bỏ đi
        database_url = database_url.strip().strip('"').strip("'")

        # Railway thường trả mysql://..., SQLAlchemy cần mysql+pymysql://...
        if database_url.startswith("mysql://"):
            database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

        return database_url

    mysql_host = os.getenv("MYSQLHOST") or os.getenv("DB_HOST")
    mysql_port = os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306")
    mysql_user = os.getenv("MYSQLUSER") or os.getenv("DB_USER") or os.getenv("DB_USERNAME", "root")
    mysql_password = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "")
    mysql_database = (
        os.getenv("MYSQLDATABASE")
        or os.getenv("MYSQL_DATABASE")
        or os.getenv("DB_DATABASE")
        or os.getenv("DB_NAME")
        or "railway"
    )

    if mysql_host:
        return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

    return "mysql+pymysql://root:@localhost:3306/attendance_dbx1"
    
class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'Attendance System')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')
    
    # Database
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_TIMEOUT', 3600))
    )
    
    # Security
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
    
    # Face Recognition
    FACE_RECOGNITION_TOLERANCE = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.6))
    FACE_DETECTION_MODEL = os.getenv('FACE_DETECTION_MODEL', 'hog')  # 'hog' or 'cnn'
    MAX_FACE_DISTANCE = float(os.getenv('MAX_FACE_DISTANCE', 0.6))
    FACE_ENCODINGS_PATH = 'face_encodings'
    
    # Camera
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
    CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', 480))
    CAMERA_FPS = int(os.getenv('CAMERA_FPS', 60))
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
    TRAIN_PATH = os.path.join(DATASET_PATH, 'train')
    BACKUP_PATH = os.path.join(BASE_DIR, 'backups')
    LOG_PATH = os.path.join(BASE_DIR, 'logs')
    STATIC_PATH = os.path.join(BASE_DIR, 'app', 'static')
    UPLOAD_PATH = os.path.join(STATIC_PATH, 'uploads')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(LOG_PATH, 'attendance.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Backup
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_INTERVAL = os.getenv('BACKUP_INTERVAL', 'daily')
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    
    # Work Schedule
    DEFAULT_SHIFT_START = '08:00'
    DEFAULT_SHIFT_END = '17:00'
    LATE_THRESHOLD_MINUTES = 15
    EARLY_LEAVE_THRESHOLD_MINUTES = 15


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production database
    SQLALCHEMY_DATABASE_URI = get_database_url()
    
    # Stronger security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_database_url()
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}

