import os

import mysql.connector
from mysql.connector import Error


MYSQL_CONFIG = {
    "host": os.getenv("PIPELINE_MYSQL_HOST", "localhost"),
    "database": os.getenv("PIPELINE_MYSQL_DATABASE", "pipeline"),
    "user": os.getenv("PIPELINE_MYSQL_USER", "root"),
    "password": os.getenv("PIPELINE_MYSQL_PASSWORD", "root"),
}


def main() -> None:
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if not conn.is_connected():
            raise RuntimeError("MySQL connection was created but is not active.")

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = int(cursor.fetchone()[0])
        print(f"Total records in posts table: {count}")
    except (Error, RuntimeError) as exc:
        print(f"Error: {exc}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
