// frontend/src/App.jsx
/**
 * Purpose: Main Application Component.
 * Responsibilities:
 * - Load user profiles on launch if JWT tokens are present.
 * - Establish client-side routes (Landing, Auth, Dashboard, Document Workspace Studio).
 * - Implement ProtectedRoute wrapper.
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchProfile } from './redux/slices/authSlice';

// Import Pages
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import DocumentStudioPage from './pages/DocumentStudioPage';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, token } = useSelector((state) => state.auth);
  
  if (!isAuthenticated || !token) {
    return <Navigate to="/auth" replace />;
  }
  return children;
};

function App() {
  const dispatch = useDispatch();
  const { token, isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    // If token exists but user details are null, fetch profile
    if (token && isAuthenticated) {
      dispatch(fetchProfile());
    }
  }, [dispatch, token, isAuthenticated]);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col font-sans">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/document/:id" 
            element={
              <ProtectedRoute>
                <DocumentStudioPage />
              </ProtectedRoute>
            } 
          />

          {/* Catch-all Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
