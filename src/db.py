"""
Database connection utilities.
"""
import os
from sqlalchemy import create_engine


def get_engine():
    """
    Get SQLAlchemy engine from DATABASE_URL environment variable.
    
    Returns:
        sqlalchemy.engine.Engine
    """
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    return create_engine(database_url)

