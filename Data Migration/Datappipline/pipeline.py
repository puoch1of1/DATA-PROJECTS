import os

import mysql.connector
import requests
from mysql.connector import Error


API_URL = "https://jsonplaceholder.typicode.com/posts"
API_TIMEOUT_SECONDS = 30
MYSQL_CONFIG = {
    "host": os.getenv("PIPELINE_MYSQL_HOST", "localhost"),
    "database": os.getenv("PIPELINE_MYSQL_DATABASE", "pipeline"),
    "user": os.getenv("PIPELINE_MYSQL_USER", "root"),
    "password": os.getenv("PIPELINE_MYSQL_PASSWORD", "root"),
}


def fetch_posts() -> list[dict]:
    api_key = os.getenv("JSONPLACEHOLDER_API_KEY")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.get(API_URL, headers=headers, timeout=API_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def main() -> None:
    posts = fetch_posts()
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if not conn.is_connected():
            raise RuntimeError("MySQL connection was created but is not active.")

        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INT PRIMARY KEY,
                user_id INT,
                title TEXT,
                body TEXT
            )
            """
        )

        payload = [
            (post["id"], post["userId"], post["title"], post["body"]) for post in posts
        ]
        cursor.executemany(
            """
            INSERT INTO posts (id, user_id, title, body)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                user_id = VALUES(user_id),
                title = VALUES(title),
                body = VALUES(body)
            """,
            payload,
        )
        conn.commit()
        print(f"Data pipeline executed successfully. Upserted {cursor.rowcount} rows.")
    except (Error, requests.RequestException, RuntimeError) as exc:
        print(f"Error: {exc}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
