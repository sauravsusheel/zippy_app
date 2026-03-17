import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUserId = localStorage.getItem('user_id');
    const storedEmployeeId = localStorage.getItem('employee_id');

    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUser({
        user_id: storedUserId,
        employee_id: storedEmployeeId,
      });
      setIsAuthenticated(true);
    }

    setLoading(false);
  }, []);

  const login = (authToken, userId, employeeId) => {
    localStorage.setItem('auth_token', authToken);
    localStorage.setItem('user_id', userId);
    localStorage.setItem('employee_id', employeeId);

    setToken(authToken);
    setUser({
      user_id: userId,
      employee_id: employeeId,
    });
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('employee_id');

    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    isAuthenticated,
    user,
    token,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
