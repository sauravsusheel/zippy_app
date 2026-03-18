"""
Face Recognition Service — DeepFace (Facenet512)
Handles face detection, embedding extraction, and comparison.

No training required. Facenet512 model downloads automatically on first use (~90MB).
"""

import numpy as np
from typing import List, Tuple, Optional
from io import BytesIO
from PIL import Image
import os
import tempfile

# ── Model config ──────────────────────────────────────────────────────────────
MODEL_NAME = "Facenet512"      # 512-dim embeddings, great accuracy/speed balance
DETECTOR_BACKEND = "opencv"    # fast, ships with opencv-python, no extra deps
COSINE_THRESHOLD = 0.30        # cosine distance threshold (lower = stricter)
#   < 0.10  → very confident match
#   0.10–0.30 → good match
#   > 0.30  → different person
# ─────────────────────────────────────────────────────────────────────────────

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✓ DeepFace loaded successfully")
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("✗ DeepFace not available — install with: pip install deepface tf-keras tensorflow")


def _image_bytes_to_temp_file(image_data: bytes) -> str:
    """Save image bytes to a temp JPEG file and return the path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        image = Image.open(BytesIO(image_data)).convert("RGB")
        image.save(tmp.name, format="JPEG", quality=95)
    finally:
        tmp.close()
    return tmp.name


def _cleanup(path: str):
    try:
        os.remove(path)
    except Exception:
        pass


def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine distance between two vectors (0 = identical)."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - float(np.dot(a, b) / (norm_a * norm_b))


# ── Public API ────────────────────────────────────────────────────────────────

def detect_face_in_image(image_data: bytes) -> bool:
    """
    Returns True if exactly one real, clear face is detected.

    Checks:
    - Confidence >= 0.85 (filters blurry/partial faces)
    - Face area >= 60x60px (rejects tiny background faces)
    - anti_spoofing=True (rejects printed photos / screen replays)
    - Exactly one face (rejects group photos)
    """
    if not DEEPFACE_AVAILABLE:
        raise RuntimeError("DeepFace is not installed. Run: pip install deepface tf-keras tensorflow")

    tmp_path = _image_bytes_to_temp_file(image_data)
    try:
        faces = DeepFace.extract_faces(
            img_path=tmp_path,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False,
            align=True,
        )

        valid_faces = [
            f for f in faces
            if f.get("confidence", 0) >= 0.85
            and f["facial_area"]["w"] >= 60
            and f["facial_area"]["h"] >= 60
        ]

        if len(valid_faces) == 0:
            print("⚠ No valid face detected (low confidence, too small, or spoof attempt)")
            return False

        if len(valid_faces) > 1:
            print(f"⚠ Multiple faces detected ({len(valid_faces)}), rejecting")
            return False

        return True

    except Exception as e:
        print(f"Face detection error: {e}")
        return False
    finally:
        _cleanup(tmp_path)


def encode_face_from_image(image_data: bytes) -> Optional[List[float]]:
    """
    Extract a 512-dimensional face embedding using Facenet512.
    Returns None if no face found or extraction fails.
    """
    if not DEEPFACE_AVAILABLE:
        raise RuntimeError("DeepFace is not installed. Run: pip install deepface tf-keras tensorflow")

    tmp_path = _image_bytes_to_temp_file(image_data)
    try:
        result = DeepFace.represent(
            img_path=tmp_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )

        if not result:
            return None

        return result[0]["embedding"]  # list of 512 floats

    except ValueError as e:
        print(f"No face found during encoding: {e}")
        return None
    except Exception as e:
        print(f"Face encoding error: {e}")
        return None
    finally:
        _cleanup(tmp_path)


def compare_faces(
    known_encoding: List[float],
    test_encoding: List[float],
) -> Tuple[bool, float]:
    """
    Compare two face embeddings.
    Returns (is_match: bool, cosine_distance: float).
    """
    known = np.array(known_encoding)
    test = np.array(test_encoding)
    distance = _cosine_distance(known, test)
    return distance < COSINE_THRESHOLD, distance


def find_best_match(
    test_encoding: List[float],
    known_encodings: List[List[float]],
) -> Tuple[Optional[int], float]:
    """
    Find the closest matching embedding from a list.
    Returns (index_of_best_match or None, best_distance).
    """
    if not known_encodings:
        return None, 1.0

    test = np.array(test_encoding)
    distances = np.array([
        _cosine_distance(np.array(enc), test)
        for enc in known_encodings
    ])

    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])

    print(f"  Best match distance: {best_dist:.4f} (threshold: {COSINE_THRESHOLD})")

    if best_dist < COSINE_THRESHOLD:
        return best_idx, best_dist

    return None, best_dist
