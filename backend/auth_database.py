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
    """Initialize authentication database with users and face encodings tables"""
    conn = sqlite3.connect(AUTH_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            company_unique_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create face_encodings table to store multiple encodings per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            face_encoding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee_id ON users(employee_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON face_encodings(user_id)
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
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            # Add additional face encoding for existing user
            encoding_json = json.dumps(face_encoding)
            cursor.execute("""
                INSERT INTO face_encodings (user_id, face_encoding)
                VALUES (?, ?)
            """, (user_id, encoding_json))
            conn.commit()
            conn.close()
            return {
                "success": True,
                "message": "Additional face encoding registered successfully",
                "user_id": user_id
            }
        
        # Create new user
        cursor.execute("""
            INSERT INTO users (employee_id, company_unique_id)
            VALUES (?, ?)
        """, (employee_id, company_unique_id))
        
        user_id = cursor.lastrowid
        
        # Add first face encoding
        encoding_json = json.dumps(face_encoding)
        cursor.execute("""
            INSERT INTO face_encodings (user_id, face_encoding)
            VALUES (?, ?)
        """, (user_id, encoding_json))
        
        conn.commit()
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
    Retrieve user and all face encodings by employee ID
    
    Args:
        employee_id: Employee identifier
    
    Returns:
        User dict with list of face encodings or None
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, company_unique_id, created_at
            FROM users WHERE employee_id = ?
        """, (employee_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        user_id = row[0]
        
        # Get all face encodings for this user
        cursor.execute("""
            SELECT face_encoding FROM face_encodings
            WHERE user_id = ?
            ORDER BY created_at ASC
        """, (user_id,))
        
        encodings = [json.loads(enc[0]) for enc in cursor.fetchall()]
        conn.close()
        
        return {
            "id": user_id,
            "employee_id": row[1],
            "company_unique_id": row[2],
            "face_encodings": encodings,
            "created_at": row[3]
        }
    
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None

def get_all_users() -> List[Dict]:
    """
    Retrieve all registered users with their face encodings
    
    Returns:
        List of user dicts with face encodings
    """
    try:
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, employee_id, company_unique_id, created_at
            FROM users
        """)
        
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            user_id = row[0]
            
            # Get all face encodings for this user
            cursor.execute("""
                SELECT face_encoding FROM face_encodings
                WHERE user_id = ?
                ORDER BY created_at ASC
            """, (user_id,))
            
            encodings = [json.loads(enc[0]) for enc in cursor.fetchall()]
            
            users.append({
                "id": user_id,
                "employee_id": row[1],
                "company_unique_id": row[2],
                "face_encodings": encodings,
                "created_at": row[3]
            })
        
        conn.close()
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
