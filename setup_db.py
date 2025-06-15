import os
import pymysql
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash

load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

# Timezone setup
eastern = pytz.timezone('US/Eastern')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(eastern))
    resorts = db.relationship('UserResort', backref='user', lazy=True)

class Resort(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    county = db.Column(db.String(100))
    resort_name = db.Column(db.String(200), nullable=False)
    picture_local_address = db.Column(db.String(500))
    resort_type = db.Column(db.String(50), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_resorts = db.relationship('UserResort', backref='resort', lazy=True)

class UserResort(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(eastern))
    recommendation = db.Column(db.Integer)
    expenditure = db.Column(db.Float)
    comment = db.Column(db.Text)

def get_db_config():
    """Return database configuration dictionary"""
    return {
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_NAME': os.getenv('DB_NAME')
    }

def initialize_database():
    """Initialize the database and create tables"""
    admin_conn = None
    try:
        # Print environment variables for debugging
        print("Checking environment variables...")
        print("*"*100)
        root_user = os.getenv('MYSQL_ROOT_USER')
        root_password = os.getenv('MYSQL_ROOT_PASSWORD')
        db_name = os.getenv('DB_NAME', 'TravelHub')
        
        if not root_user or not root_password:
            raise ValueError("Missing required environment variables: MYSQL_ROOT_USER or MYSQL_ROOT_PASSWORD")
            
        print(f"MYSQL_ROOT_USER: {root_user}")
        print(f"MYSQL_ROOT_PASSWORD: {'*' * len(root_password) if root_password else 'None'}")
        print(f"DB_NAME: {db_name}")
        print("*"*100)

        # Create database connection (using system root privileges)
        print("\nConnecting to MySQL...")
        try:
            # 首先尝试使用 localhost
            admin_conn = pymysql.connect(
                host='localhost',
                user=root_user,
                password=root_password,
                charset='utf8mb4'
            )
        except pymysql.Error as e:
            print(f"Failed to connect using localhost: {str(e)}")
            print("Trying with 127.0.0.1...")
            # 如果失败，尝试使用 127.0.0.1
            admin_conn = pymysql.connect(
                host='127.0.0.1',
                user=root_user,
                password=root_password,
                charset='utf8mb4'
            )
        
        print("Connected to MySQL successfully")

        with admin_conn.cursor() as cursor:
            # Create database
            print("\nCreating database...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database {db_name} created successfully")

        admin_conn.commit()
        print("\nDatabase initialization completed successfully")

    except ValueError as ve:
        print(f"Configuration Error: {str(ve)}")
        print("Please check your .env file and make sure all required variables are set.")
    except pymysql.Error as e:
        print(f"MySQL Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your root password is correct")
        print("3. Try connecting manually with: mysql -u root -p")
        print("4. If needed, reset root password with:")
        print("   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        print("An unexpected error occurred during database initialization.")
    finally:
        if admin_conn:
            try:
                admin_conn.close()
                print("Database connection closed")
            except Exception as e:
                print(f"Error closing database connection: {str(e)}")

def init_app(app):
    """Initialize the database with the Flask app"""
    try:
        # Configure database URI using root credentials
        root_user = os.getenv('MYSQL_ROOT_USER')
        root_password = os.getenv('MYSQL_ROOT_PASSWORD')
        db_name = os.getenv('DB_NAME', 'TravelHub')
        
        if not root_user or not root_password:
            raise ValueError("Missing required environment variables: MYSQL_ROOT_USER or MYSQL_ROOT_PASSWORD")
            
        # 尝试使用 localhost 和 127.0.0.1
        try:
            app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{root_user}:{root_password}@localhost/{db_name}"
            db.init_app(app)
            with app.app_context():
                db.create_all()
        except Exception as e:
            print(f"Failed to connect using localhost: {str(e)}")
            print("Trying with 127.0.0.1...")
            app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{root_user}:{root_password}@127.0.0.1/{db_name}"
            db.init_app(app)
            with app.app_context():
                db.create_all()
        
        print("Database tables created successfully")
        
        # Check if admin user exists
        with app.app_context():
            admin = User.query.filter_by(username='root').first()
            if not admin:
                # Create admin user with secure password
                admin = User(
                    username=root_user,
                    nickname='系统管理员',
                    password=root_password,  # 建议之后修改此密码
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("已成功创建管理员账户。")
            
    except Exception as e:
        print(f"Error initializing Flask app database: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_database()