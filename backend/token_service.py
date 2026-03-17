"""
JWT Token Service
Handles token generation and validation
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import os

# Secret key for JWT (should be in environment)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "zippy-face-auth-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

def generate_token(user_id: int, employee_id: str) -> str:
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id: User ID from database
        employee_id: Employee ID
    
    Returns:
        JWT token string
    """
    try:
        payload = {
            "user_id": user_id,
            "employee_id": employee_id,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    except Exception as e:
        print(f"Error generating token: {e}")
        return None

def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def get_user_from_token(token: str) -> Optional[Dict]:
    """
    Extract user info from token
    
    Args:
        token: JWT token string
    
    Returns:
        User info dict or None
    """
    payload = verify_token(token)
    if payload:
        return {
            "user_id": payload.get("user_id"),
            "employee_id": payload.get("employee_id")
        }
    return None
