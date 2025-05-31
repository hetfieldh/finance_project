import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_if_not_set')
    DATABASE = {
        'dbname': os.getenv('DB_NAME', 'your_default_db'),
        'user': os.getenv('DB_USER', 'your_default_user'),
        'password': os.getenv('DB_PASSWORD', 'your_default_password'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
