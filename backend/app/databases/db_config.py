import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The Connection String tells SQLAlchemy exactly how to reach our Docker container.
# Format: dialect://username:password@host:port/database_name

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:postgres@localhost:5432/postgres")

# The Engine is the core connection pool. 
engine = create_engine(DATABASE_URL)

# A Session is a temporary workspace for your queries (like a transaction).
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

# All our future Table models will inherit from this Base class.
Base = declarative_base()

# A "Dependency" function to give our FastAPI routes a temporary DB connection, 
# and automatically close it when they are done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
