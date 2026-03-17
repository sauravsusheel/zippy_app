import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import '../styles/Auth.css';

function Login({ onLoginSuccess }) {
  const [employeeId, setEmployeeId] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const webcamRef = useRef(null);

  // Auto-start camera when login page loads
  useEffect(() => {
    setShowCamera(true);
  }, []);

  const handleCaptureFace = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setCapturedImage(imageSrc);
      setShowCamera(false);
      
      // Auto-verify after capture
      setTimeout(() => handleVerifyFace(imageSrc), 500);
    }
  };

  const handleVerifyFace = async (imageToVerify = capturedImage) => {
    if (!imageToVerify) {
      setError('Please capture a face image');
      return;
    }

    setVerifying(true);
    setError(null);

    try {
      // Remove data:image/jpeg;base64, prefix if present
      const base64Image = imageToVerify.includes(',') 
        ? imageToVerify.split(',')[1] 
        : imageToVerify;

      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          face_image: base64Image,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Face recognized! Logging in...');
        
        // Store token in localStorage
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('employee_id', data.employee_id);
        
        // Redirect to dashboard after 1 second
        setTimeout(() => {
          onLoginSuccess(data.token);
        }, 1000);
      } else {
        setError(data.error || 'Face not recognized. Please try again.');
        setCapturedImage(null);
        setShowCamera(true);
      }
    } catch (err) {
      setError('Network error: ' + err.message);
      setCapturedImage(null);
      setShowCamera(true);
    } finally {
      setVerifying(false);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setShowCamera(true);
    setError(null);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Zippy - Face Login</h1>
        <p className="auth-subtitle">Verify your face to access Zippy</p>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <div className="auth-form">
          {showCamera && !capturedImage && (
            <div className="form-group">
              <label>Position your face in the camera</label>
              <div className="camera-container">
                <Webcam
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width={300}
                  height={300}
                  className="webcam"
                />
                <div className="camera-controls">
                  <button
                    type="button"
                    className="btn-success"
                    onClick={handleCaptureFace}
                    disabled={verifying}
                  >
                    📸 Capture Face
                  </button>
                </div>
              </div>
            </div>
          )}

          {capturedImage && (
            <div className="form-group">
              <label>Captured Face</label>
              <div className="captured-image-container">
                <img src={capturedImage} alt="Captured face" className="captured-image" />
                {verifying && (
                  <div style={{ textAlign: 'center', marginTop: '10px' }}>
                    <div className="loading-spinner"></div>
                    <p style={{ color: '#667eea', marginTop: '10px' }}>Verifying face...</p>
                  </div>
                )}
                {!verifying && (
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={handleRetake}
                  >
                    🔄 Retake Photo
                  </button>
                )}
              </div>
            </div>
          )}

          {!showCamera && !capturedImage && !verifying && (
            <button
              type="button"
              className="btn-primary btn-large"
              onClick={() => setShowCamera(true)}
            >
              📷 Open Camera
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
