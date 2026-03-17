"""
Face Recognition Service
Handles face detection, encoding, and comparison
"""

import numpy as np
from typing import List, Tuple, Optional
import base64
from io import BytesIO
from PIL import Image
import hashlib

# Face recognition tolerance (lower = stricter matching)
# Standard face_recognition library uses 0.6 as default
# We use 0.5 for stricter matching to prevent false positives
# For hash-based fallback, we use 0.15 (15% difference threshold)
FACE_MATCH_TOLERANCE = 0.5
HASH_MATCH_TOLERANCE = 0.15  # For fallback hash-based matching

# Try to import face_recognition, fall back to simple hash-based matching
try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face-recognition not available, using simplified face matching")

def encode_face_from_image(image_data: bytes) -> Optional[List[float]]:
    """
    Extract face encoding from image bytes
    
    Args:
        image_data: Image bytes (JPEG/PNG)
    
    Returns:
        Face encoding array or None if no face detected
    """
    try:
        # Convert bytes to image
        image = Image.open(BytesIO(image_data))
        image_array = np.array(image)
        
        if FACE_RECOGNITION_AVAILABLE:
            # Use face_recognition library if available
            # Convert RGB to BGR for OpenCV (if needed)
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Detect faces in image
            face_locations = face_recognition.face_locations(image_array, model="hog")
            
            if not face_locations:
                return None
            
            # Get face encoding (use first face if multiple detected)
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            
            if not face_encodings:
                return None
            
            # Return first face encoding as list
            return face_encodings[0].tolist()
        else:
            # Fallback: Use image hash as encoding with strict matching
            # This is a simplified approach for testing without dlib
            # Validate that we have a valid image
            if image_array.size == 0:
                return None
            
            # Use multiple hash methods for better encoding
            import hashlib
            
            # Resize image to standard size for consistent hashing
            from PIL import Image as PILImage
            img = PILImage.fromarray(image_array.astype('uint8'))
            img_resized = img.resize((64, 64))
            img_array = np.array(img_resized)
            
            # Create multiple hashes for robustness
            hash1 = hashlib.sha256(img_array.tobytes()).digest()
            hash2 = hashlib.md5(img_array.tobytes()).digest()
            
            # Combine hashes into 128-dimensional vector
            encoding = []
            for i in range(64):
                byte_val1 = hash1[i % len(hash1)]
                byte_val2 = hash2[i % len(hash2)]
                # Normalize to -1 to 1 range
                encoding.append((byte_val1 / 128.0) - 1.0)
                encoding.append((byte_val2 / 128.0) - 1.0)
            
            return encoding
    
    except Exception as e:
        print(f"Error encoding face: {e}")
        return None

def compare_faces(known_encoding: List[float], test_encoding: List[float]) -> Tuple[bool, float]:
    """
    Compare two face encodings
    
    Args:
        known_encoding: Stored face encoding
        test_encoding: Face encoding to test
    
    Returns:
        Tuple of (match: bool, distance: float)
    """
    try:
        # Convert lists to numpy arrays
        known_array = np.array(known_encoding)
        test_array = np.array(test_encoding)
        
        if FACE_RECOGNITION_AVAILABLE:
            # Calculate face distance using face_recognition
            distance = face_recognition.face_distance([known_array], test_array)[0]
            match = distance < FACE_MATCH_TOLERANCE
        else:
            # Fallback: Calculate Euclidean distance with strict threshold
            distance = np.linalg.norm(known_array - test_array)
            # Normalize distance for hash-based matching
            distance = distance / (128.0 * 2.0)  # Normalize by encoding size
            match = distance < HASH_MATCH_TOLERANCE
        
        return match, float(distance)
    
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return False, 1.0

def detect_face_in_image(image_data: bytes) -> bool:
    """
    Check if a face is detected in image
    
    Args:
        image_data: Image bytes
    
    Returns:
        True if face detected, False otherwise
    """
    try:
        image = Image.open(BytesIO(image_data))
        image_array = np.array(image)
        
        if FACE_RECOGNITION_AVAILABLE:
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            face_locations = face_recognition.face_locations(image_array, model="hog")
            return len(face_locations) > 0
        else:
            # Fallback: Check if image has reasonable size and content
            # This is a simplified check - requires face-recognition for real detection
            if image_array.size == 0:
                return False
            
            # Check if image is large enough to contain a face
            if image_array.shape[0] < 50 or image_array.shape[1] < 50:
                return False
            
            # Check if image has reasonable variance (not blank)
            if len(image_array.shape) == 3:
                variance = np.var(image_array)
            else:
                variance = np.var(image_array)
            
            return variance > 100  # Image has enough content
    
    except Exception as e:
        print(f"Error detecting face: {e}")
        return False

def find_best_match(test_encoding: List[float], known_encodings: List[List[float]]) -> Tuple[Optional[int], float]:
    """
    Find best matching face from list of known encodings
    
    Args:
        test_encoding: Face encoding to match
        known_encodings: List of known face encodings
    
    Returns:
        Tuple of (index of best match or None, distance of best match)
    """
    try:
        if not known_encodings:
            return None, 1.0
        
        test_array = np.array(test_encoding)
        known_arrays = np.array(known_encodings)
        
        if FACE_RECOGNITION_AVAILABLE:
            # Calculate distances to all known faces
            distances = face_recognition.face_distance(known_arrays, test_array)
            tolerance = FACE_MATCH_TOLERANCE
        else:
            # Fallback: Calculate Euclidean distances with strict threshold
            distances = np.array([np.linalg.norm(known_array - test_array) for known_array in known_arrays])
            # Normalize distances for hash-based matching
            distances = distances / (128.0 * 2.0)
            tolerance = HASH_MATCH_TOLERANCE
        
        # Find best match
        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]
        
        # Check if it's within tolerance
        if best_distance < tolerance:
            return best_match_index, float(best_distance)
        
        return None, float(best_distance)
    
    except Exception as e:
        print(f"Error finding best match: {e}")
        return None, 1.0
