import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from auth import hash_password
from models import UserRole

def create_admin_user():
    name = "Ali Admin"
    email = "Aliadmin@payfast.com"
    cnic = "00000-0000000-0"
    password = "Aliadmin123" 
    
    hashed_password = hash_password(password)
    
    connection = get_db_connection()
    if connection is None:
        print("Database connection failed")
        return
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            print("Admin user already exists")
            return
        
        cursor.execute(
            "INSERT INTO users (name, email, cnic, password, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, cnic, hashed_password, UserRole.ADMIN.value)
        )
        connection.commit()
        
        print("Admin user created successfully")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_admin_user()