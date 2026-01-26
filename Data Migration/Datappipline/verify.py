import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        database='pipeline',
        user='root',
        password='root'
    )
    
    if conn.is_connected():
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()
        print(f"Total records in posts table: {count[0]}")
        
        cursor.close()
        conn.close()
        
except Error as e:
    print(f"Error: {e}")
