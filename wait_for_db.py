import time
import psycopg2
import os
import sys

db_name = os.environ.get("POSTGRES_DB")
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")

def check_db():
    try:
        # Connect to default postgres DB
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check DB exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        db_exists = cur.fetchone() is not None

        # Check user exists
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (db_user,))
        user_exists = cur.fetchone() is not None

        cur.close()
        conn.close()
        return db_exists and user_exists

    except psycopg2.OperationalError:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Used for healthcheck
        sys.exit(0 if check_db() else 1)

    while not check_db():
        print(f"⏳ Waiting for DB='{db_name}' and USER='{db_user}'...")
        time.sleep(1)

    print(f"✅ Database '{db_name}' and user '{db_user}' are ready!")
