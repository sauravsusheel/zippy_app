"""
Face Recognition Authentication Database Module
Handles user registration and face encoding storage
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, List
import numpy as np

AUTH_DB_PATH = "auth_users.db"

def init_auth_database():
    """Initialize authentication database with users table"""
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            company_unique_id TEXT NOT NULL,
            face_encoding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee_id ON users(employee_id)
    """)
    
    conn.commit()
    conn.close()
    print("✓ Authentication database initialized")

def register_user(employee_id: str, company_unique_id: str, face_encoding: List[float]) -> Dict:
    """
    Register a new user with face encoding
    
    Args:
        employee_id: Unique employee identifier
        company_unique_id: Company identifier
        face_encoding: Face encoding array from face_recognition library
    
    Returns:
        Dict with success status and message
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        # Check if employee already exists
        cursor.execute("SELECT id FROM users WHERE employee_id = ?", (employee_id,))
        if cursor.fetchone():
            conn.close()
            return {"success": False, "error": "Employee ID already registered"}
        
        # Convert face encoding to JSON string for storage
        encoding_json = json.dumps(face_encoding)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (employee_id, company_unique_id, face_encoding)
            VALUES (?, ?, ?)
        """, (employee_id, company_unique_id, encoding_json))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_user_by_employee_id(employee_id: str) -> Optional[Dict]:
    """
    Retrieve user and face encoding by employee ID
    
    Args:
        employee_id: Employee identifier
    
    Returns:
        User dict with face encoding or None
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, company_unique_id, face_encoding, created_at
            FROM users WHERE employee_id = ?
        """, (employee_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "employee_id": row[1],
            "company_unique_id": row[2],
            "face_encoding": json.loads(row[3]),
            "created_at": row[4]
        }
    
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None

def get_all_users() -> List[Dict]:
    """
    Retrieve all registered users
    
    Returns:
        List of user dicts with face encodings
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, company_unique_id, face_encoding, created_at
            FROM users
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "employee_id": row[1],
                "company_unique_id": row[2],
                "face_encoding": json.loads(row[3]),
                "created_at": row[4]
            })
        
        return users
    
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []

def delete_user(employee_id: str) -> Dict:
    """
    Delete a user by employee ID
    
    Args:
        employee_id: Employee identifier
    
    Returns:
        Dict with success status
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE employee_id = ?", (employee_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "error": "User not found"}
        
        conn.close()
        return {"success": True, "message": "User deleted successfully"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    init_auth_database()
