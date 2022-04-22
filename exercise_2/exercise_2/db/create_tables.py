"""Script to create DB tables."""
import logging
import os

from model_tables import Base
from sqlalchemy import create_engine

# Set up Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# POSTGRES_DB = os.getenv("POSTGRES_DB")
# POSTGRES_HOST = os.getenv("POSTGRES_HOST")
# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

POSTGRES_DB = "postgres"
POSTGRES_HOST = "mutt-db"  # "localhost"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"

DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


def main():
    """Program entrypoint."""
    # Logic to create tables goes here.
    # https://docs.sqlalchemy.org/en/14/orm/tutorial.html#create-a-schema

    logger.info("Creating connection to Local Postgres DB...")
    logger.info("Connection established")
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)
    logger.info("Tables Created!")


if __name__ == "__main__":
    main()
