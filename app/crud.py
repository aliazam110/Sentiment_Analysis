import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
from database import get_db_connection
from models import UserRole, ReviewResponse
import json

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    connection = get_db_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    except Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_all_users() -> List[Dict[str, Any]]:
    connection = get_db_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, name, email, cnic, role, created_at FROM users ORDER BY created_at DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_all_reviews_with_user_info() -> List[Dict[str, Any]]:
    connection = get_db_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get all reviews with user information
        cursor.execute(
            """
            SELECT r.id, r.user_id, r.review_text, r.sentiment_results, r.created_at, 
                   u.name as user_name, u.email as user_email
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
            """
        )
        reviews_data = cursor.fetchall()
        
        # Parse JSON results for each review
        reviews = []
        for review_data in reviews_data:
            review_data['sentiment_results'] = json.loads(review_data['sentiment_results'])
            reviews.append(review_data)
        
        return reviews
    except Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def create_review(user_id: int, review_text: str, sentiment_results: Dict[str, Any]) -> Optional[ReviewResponse]:
    connection = get_db_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        results_json = json.dumps(sentiment_results)
        
        cursor.execute(
            "INSERT INTO reviews (user_id, review_text, sentiment_results) VALUES (%s, %s, %s)",
            (user_id, review_text, results_json)
        )
        connection.commit()
        
        review_id = cursor.lastrowid
        cursor.execute(
            "SELECT * FROM reviews WHERE id = %s",
            (review_id,)
        )
        review_data = cursor.fetchone()
        
        review_data['sentiment_results'] = json.loads(review_data['sentiment_results'])
        
        return ReviewResponse(**review_data)
    except Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()