import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise  

def init_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute()
                conn.commit()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise

def store_tokens(broadcaster_id: str, refresh_token: str, access_token: Optional[str] = None, expires_at: Optional[int] = None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(, (broadcaster_id, refresh_token, access_token, expires_at))
                conn.commit()
    except Exception as e:
        logger.error(f"Error while storing tokens: {e}")
        raise

def get_tokens(broadcaster_id: str) -> Optional[Dict[str, Any]]:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tokens WHERE broadcaster_id = %s;", (broadcaster_id,))
                return cur.fetchone()  
    except Exception as e:
        logger.error(f"Error while retrieving tokens: {e}")
        raise 

def delete_tokens(broadcaster_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tokens WHERE broadcaster_id = %s;", (broadcaster_id,))
                conn.commit()
    except Exception as e:
        logger.error(f"Error while deleting tokens: {e}")
        raise