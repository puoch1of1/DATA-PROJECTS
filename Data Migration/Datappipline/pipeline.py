import requests
import mysql.connector
from mysql.connector import Error

# 1. API endpoint
API_URL = "https://jsonplaceholder.typicode.com/posts"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

# 2. Fetch data from API
response = requests.get(API_URL)
response.raise_for_status()  # fails fast if API breaks
posts = response.json()

# 3. Connect to MySQL database
try:
    conn = mysql.connector.connect(
        host='localhost',  # Change if your MySQL server is on a different host
        database='pipeline',  # Your database name
        user='root',  # Your MySQL username
        password='root'  # Your MySQL password
    )
    
    if conn.is_connected():
        cursor = conn.cursor()

        # 4. Create table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT PRIMARY KEY,
            user_id INT,
            title TEXT,
            body TEXT
        )
        """)

        # 5. Insert data
        for post in posts:
            cursor.execute("""
            INSERT INTO posts (id, user_id, title, body)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            user_id = VALUES(user_id),
            title = VALUES(title),
            body = VALUES(body)
            """, (
                post["id"],
                post["userId"],
                post["title"],
                post["body"]
            ))

        # 6. Commit and close
        conn.commit()
        print("Data pipeline executed successfully.")

except Error as e:
    print(f"Error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()