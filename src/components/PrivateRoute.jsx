import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>;

  if (!user) {
    return (
      <div style={{ textAlign: 'center', marginTop: '4rem', color: '#e6f7ff' }}>
        <h2>🔒 Access Denied</h2>
        <p>You need to <a href="/login" style={{ color: '#00eaff' }}>log in</a> or <a href="/signup" style={{ color: '#00eaff' }}>sign up</a> to view this page.</p>
      </div>
    );
  }

  return children;
};

export default PrivateRoute;