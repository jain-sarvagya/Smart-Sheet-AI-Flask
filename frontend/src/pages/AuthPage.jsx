// frontend/src/pages/AuthPage.jsx
/**
 * Purpose: Authenticate Users (Sign In / Sign Up).
 * Responsibilities:
 * - Toggle state between Login and Registration forms.
 * - Capture user inputs (name, email, password).
 * - Dispatch loginUser and registerUser Redux thunks.
 * - Redirect to /dashboard upon successful verification.
 * - Render detailed validation error message prompts.
 */

import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser, registerUser, clearError } from '../redux/slices/authSlice';
import { Layers, Sparkles, AlertCircle, Loader } from 'lucide-react';

function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });

  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const { loading, error, isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    // If already authenticated, redirect straight to dashboard
    if (isAuthenticated) {
      navigate('/dashboard');
    }
    // Clear errors when toggling modes
    dispatch(clearError());
  }, [isAuthenticated, navigate, isLogin, dispatch]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) {
      dispatch(loginUser({ email: formData.email, password: formData.password }));
    } else {
      dispatch(registerUser(formData));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center grid-bg px-4 relative">
      {/* Glow Orbs */}
      <div className="absolute w-[400px] h-[400px] rounded-full bg-indigo-500/10 blur-[80px] top-[20%] left-[30%] pointer-events-none" />

      <div className="w-full max-w-md z-10">
        
        {/* Brand Header */}
        <div className="flex flex-col items-center mb-8 text-center">
          <Link to="/" className="flex items-center gap-2 mb-3">
            <div className="bg-gradient-to-tr from-indigo-500 to-purple-600 p-2 rounded-xl shadow-glow-primary">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">Smart-Sheet AI</span>
          </Link>
          <p className="text-gray-400 text-sm">
            {isLogin ? "Welcome back! Sign in to access your sheets." : "Create your account and start study generation."}
          </p>
        </div>

        {/* Auth Panel Card */}
        <div className="glass-panel p-8 rounded-2xl shadow-2xl relative border-white/10">
          
          {/* Validation Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-300 text-sm">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Authentication failed</p>
                <p className="text-red-400/90 text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name field (Registration only) */}
            {!isLogin && (
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Full Name</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required={!isLogin}
                  placeholder="John Doe"
                  className="w-full bg-gray-900/50 border border-gray-700/60 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm focus:outline-none transition-all"
                />
              </div>
            )}

            {/* Email field */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Email Address</label>
              <input 
                type="email" 
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
                className="w-full bg-gray-900/50 border border-gray-700/60 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm focus:outline-none transition-all"
              />
            </div>

            {/* Password field */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Password</label>
              <input 
                type="password" 
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="••••••••"
                className="w-full bg-gray-900/50 border border-gray-700/60 focus:border-indigo-500 rounded-xl px-4 py-3 text-sm focus:outline-none transition-all"
              />
            </div>

            {/* Submit Button */}
            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 transform active:scale-[0.98] transition-all shadow-glow-primary disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" /> Processing...
                </>
              ) : (
                <>
                  {isLogin ? "Sign In" : "Create Account"} <Sparkles className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Link */}
          <div className="mt-8 text-center text-sm text-gray-400">
            {isLogin ? "New to Smart-Sheet?" : "Already have an account?"}{' '}
            <button 
              onClick={() => setIsLogin(!isLogin)} 
              className="text-indigo-400 font-semibold hover:underline hover:text-indigo-300 transition-all"
            >
              {isLogin ? "Sign Up Free" : "Log In"}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default AuthPage;
