import React, { useState, useEffect } from 'react';
import './App.css';
import QueryInput from './components/QueryInput';
import Dashboard from './components/Dashboard';
import DatasetUpload from './components/DatasetUpload';
import DatasetPreview from './components/DatasetPreview';
import Signup from './pages/Signup';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import { processQuery } from './services/api';

function AppContent() {
  const { isAuthenticated, loading: authLoading, login, logout } = useAuth();
  const [showSignup, setShowSignup] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);

  // Fetch active dataset on mount (only if authenticated)
  useEffect(() => {
    if (isAuthenticated) {
      fetchActiveDataset();
    }
  }, [isAuthenticated]);

  const fetchActiveDataset = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/active-dataset');
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setActiveDataset(data);
        }
      }
    } catch (err) {
      console.error('Failed to fetch active dataset:', err);
    }
  };

  const handleUploadSuccess = (uploadData) => {
    setActiveDataset({
      table_name: uploadData.table_name,
      file_name: uploadData.file_name,
      rows: uploadData.rows,
      columns: uploadData.columns,
      schema: uploadData.schema,
      uploaded: uploadData.file_name !== null
    });
    setDashboardData(null);
  };

  const handleQuery = async (query) => {
    setDashboardLoading(true);
    setError(null);
    
    try {
      const result = await processQuery(query, activeDataset?.table_name);
      
      if (result.success) {
        // Add the query to the result so Dashboard can use it
        setDashboardData({ ...result, query });
        setQueryHistory(prev => [...prev, { query, timestamp: new Date() }]);
      } else {
        setError(result.error || 'Failed to process query');
      }
    } catch (err) {
      setError('Network error: Could not connect to backend');
    } finally {
      setDashboardLoading(false);
    }
  };

  const handleSignupSuccess = () => {
    setShowSignup(false);
  };

  const handleLoginSuccess = (token) => {
    const userId = localStorage.getItem('user_id');
    const employeeId = localStorage.getItem('employee_id');
    login(token, userId, employeeId);
  };

  const handleLogout = () => {
    logout();
    setDashboardData(null);
    setActiveDataset(null);
  };

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication pages if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        {showSignup ? (
          <Signup onSignupSuccess={handleSignupSuccess} />
        ) : (
          <Login onLoginSuccess={handleLoginSuccess} />
        )}
        {!showSignup && (
          <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
            <p>Don't have an account? <button 
              onClick={() => setShowSignup(true)}
              style={{ background: 'none', border: 'none', color: '#667eea', cursor: 'pointer', fontWeight: 'bold' }}
            >
              Sign up here
            </button></p>
          </div>
        )}
        {showSignup && (
          <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
            <p>Already have an account? <button 
              onClick={() => setShowSignup(false)}
              style={{ background: 'none', border: 'none', color: '#667eea', cursor: 'pointer', fontWeight: 'bold' }}
            >
              Log in here
            </button></p>
          </div>
        )}
      </>
    );
  }

  // Show dashboard if authenticated
  return (
    <div className="App">
      <header className="app-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <h1>Zippy</h1>
          <button 
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              background: '#ff6b6b',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Logout
          </button>
        </div>
        <p>Upload your data and explore insights using natural language queries</p>
      </header>

      <main className="app-main">
        <DatasetUpload 
          onUploadSuccess={handleUploadSuccess}
          activeDataset={activeDataset}
        />

        <DatasetPreview activeDataset={activeDataset} />

        <QueryInput 
          onSubmit={handleQuery} 
          loading={dashboardLoading}
        />

        {error && (
          <div className="error-message">
            <span>⚠️</span>
            <div>
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {dashboardLoading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing your query and generating dashboard...</p>
          </div>
        )}

        {dashboardData && !dashboardLoading && (
          <Dashboard data={dashboardData} />
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by Google Gemini AI • Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
