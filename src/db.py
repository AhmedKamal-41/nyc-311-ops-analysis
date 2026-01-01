"""
Database connection utilities.
"""
from sqlalchemy import create_engine
from src.config import get_database_url


def get_engine():
    """
    Get SQLAlchemy engine from DATABASE_URL.
    
    Returns:
        sqlalchemy.engine.Engine
    """
    database_url = get_database_url()
    return create_engine(database_url)

