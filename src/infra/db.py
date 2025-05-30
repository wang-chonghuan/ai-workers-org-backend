# d:\0-dev\0-finley\finley2\finley2-backend\src\infra\db.py
import os
import urllib.parse
from dotenv import load_dotenv

# Attempt to load .env file from standard locations relative to this file or project root
# This helps in development environments
dotenv_path_src = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path_project_root = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

if os.path.exists(dotenv_path_src):
    load_dotenv(dotenv_path_src)
elif os.path.exists(dotenv_path_project_root):
    load_dotenv(dotenv_path_project_root)
else:
    # Fallback: load_dotenv will search in current working directory or parent directories
    load_dotenv()

def get_supabase_db_url():
    """
    Constructs the Supabase DB URL using new parameters, with environment variables taking precedence.
    The password from the original reasoning_agent.py is used as a fallback if SUPABASE_DB_PASSWORD is not set.
    """
    # New connection parameters (USER provided)
    default_db_host = "aws-0-eu-west-1.pooler.supabase.com"
    default_db_port = "5432"
    default_db_name = "postgres"
    default_db_user = "postgres.ykjjdlscllhpypnjzrby"
    # Password from original reasoning_agent.py (as per "密码不变" - password unchanged)
    default_raw_db_password = "Nq&fY#5!zVr&5@y"

    db_host = os.getenv("SUPABASE_DB_HOST", default_db_host)
    db_port = os.getenv("SUPABASE_DB_PORT", default_db_port)
    db_name = os.getenv("SUPABASE_DB_NAME", default_db_name)
    db_user = os.getenv("SUPABASE_DB_USER", default_db_user)
    raw_db_password = os.getenv("SUPABASE_DB_PASSWORD", default_raw_db_password)

    if not raw_db_password:
        raise ValueError("Database password is not configured. Please set the SUPABASE_DB_PASSWORD environment variable.")

    encoded_db_password = urllib.parse.quote_plus(raw_db_password)

    # Construct the Supabase DB URL with psycopg driver scheme
    # The user also mentioned pool_mode: session. For Supabase Pooler, the standard connection string is usually sufficient.
    db_url = f"postgresql+psycopg://{db_user}:{encoded_db_password}@{db_host}:{db_port}/{db_name}"

    return db_url

if __name__ == '__main__':
    try:
        url = get_supabase_db_url()
        print(f"Generated Supabase DB URL: {url}")
        print("This script can be run to verify DB URL generation.")
        print("To test the actual connection, you would typically use a library like SQLAlchemy:")
        print("  Ensure 'sqlalchemy' and 'psycopg2-binary' (or 'psycopg') are installed.")
        print("  Example (uncomment to run):")
        # from sqlalchemy import create_engine, text
        # try:
        #     engine = create_engine(url)
        #     with engine.connect() as connection:
        #         result = connection.execute(text("SELECT 1 AS connection_test"))
        #         print(f"Database connection successful. Test query result: {result.scalar_one()}")
        # except Exception as e:
        #     print(f"Database connection failed: {e}")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
