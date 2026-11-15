import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

# Load credentials from .env located in the parent project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

db_pool = pooling.MySQLConnectionPool(
    pool_name="acadendora_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "admin123"),
    database=os.getenv("DB_NAME", "acadendora_db"),
    port=int(os.getenv("DB_PORT", 3306)),
    autocommit=False  # Required for explicit ACID transactions
)

def get_connection():
    """Returns an active MySQL connection from the pool."""
    return db_pool.get_connection()