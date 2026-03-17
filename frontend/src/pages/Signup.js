import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import '../styles/Auth.css';

function Signup({ onSignupSuccess }) {
  const [employeeId, setEmployeeId] = useState('');
  const [companyId, setCompanyId] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const webcamRef = useRef(null);

  const handleCaptureFace = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setCapturedImage(imageSrc);
      setShowCamera(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!employeeId || !companyId) {
      setError('Please fill in all fields');
      return;
    }

    if (!capturedImage) {
      setError('Please capture a face image');
      return;
    }

    setLoading(true);

    try {
      // Remove data:image/jpeg;base64, prefix if present
      const base64Image = capturedImage.includes(',') 
        ? capturedImage.split(',')[1] 
        : capturedImage;

      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_id: employeeId,
          company_unique_id: companyId,
          face_image: base64Image,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('Registration successful! You can now login with your face.');
        setEmployeeId('');
        setCompanyId('');
        setCapturedImage(null);
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          onSignupSuccess();
        }, 2000);
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Zippy - Face Registration</h1>
        <p className="auth-subtitle">Register your face to access Zippy</p>

        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Employee ID</label>
            <input
              type="text"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              placeholder="Enter your employee ID"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Company Unique ID</label>
            <input
              type="text"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
              placeholder="Enter company ID"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Face Capture</label>
            {!showCamera && !capturedImage && (
              <button
                type="button"
                className="btn-primary"
                onClick={() => setShowCamera(true)}
                disabled={loading}
              >
                📷 Open Camera
              </button>
            )}

            {showCamera && (
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
                  >
                    📸 Capture Face
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setShowCamera(false)}
                  >
                    ✕ Cancel
                  </button>
                </div>
              </div>
            )}

            {capturedImage && (
              <div className="captured-image-container">
                <img src={capturedImage} alt="Captured face" className="captured-image" />
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setCapturedImage(null);
                    setShowCamera(true);
                  }}
                >
                  🔄 Retake Photo
                </button>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn-primary btn-large"
            disabled={loading || !capturedImage}
          >
            {loading ? '⏳ Registering...' : '✓ Complete Registration'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Signup;
