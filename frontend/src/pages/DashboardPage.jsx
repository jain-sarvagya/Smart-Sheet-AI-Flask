// frontend/src/pages/DashboardPage.jsx
/**
 * Purpose: Main User Dashboard page.
 * Responsibilities:
 * - Load dashboard stats (documents, flashcards, quizzes counts).
 * - Render file upload interface (accepts PDF).
 * - List uploaded files with processing, ready, or failed indicators.
 * - Run polling checks to refresh documents list while documents are processing.
 * - Delegate file deletion triggers.
 */

import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { logout } from '../redux/slices/authSlice';
import { fetchDocuments, uploadDocument, deleteDocument } from '../redux/slices/docSlice';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Brain, 
  HelpCircle, 
  LogOut, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader,
  Layers,
  Sparkles
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function DashboardPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { user } = useSelector((state) => state.auth);
  const { documents, loading } = useSelector((state) => state.docs);

  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [stats, setStats] = useState({
    total_documents: 0,
    total_flashcards: 0,
    total_quizzes: 0
  });

  // Fetch stats details from dashboard endpoint
  const getStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/dashboard/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data.stats);
    } catch (err) {
      console.error("Failed to load dashboard stats", err);
    }
  };

  useEffect(() => {
    dispatch(fetchDocuments());
    getStats();
  }, [dispatch]);

  // Document status polling logic
  // Triggered when at least one document is in 'processing' status
  useEffect(() => {
    const hasProcessing = documents.some(doc => doc.status === 'processing');
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      dispatch(fetchDocuments());
      getStats();
    }, 4000);

    return () => clearInterval(interval);
  }, [documents, dispatch]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadError('Only PDF files are supported.');
      return;
    }

    setUploadError(null);
    setUploadLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await dispatch(uploadDocument(formData)).unwrap();
      getStats(); // refresh counts
    } catch (err) {
      setUploadError(err || 'Failed to upload document.');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDelete = async (docId, e) => {
    e.preventDefault(); // prevent navigation
    if (window.confirm("Are you sure you want to delete this document and all its study assets?")) {
      try {
        await dispatch(deleteDocument(docId)).unwrap();
        getStats(); // refresh counts
      } catch (err) {
        console.error("Delete failed", err);
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col grid-bg pb-12">
      
      {/* Top Header Navbar */}
      <header className="w-full border-b border-gray-800/60 bg-gray-950/70 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-tr from-indigo-500 to-purple-600 p-1.5 rounded-lg">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">Smart-Sheet AI</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold">{user?.name}</p>
              <p className="text-xs text-gray-400">{user?.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              className="flex items-center gap-2 bg-gray-900 hover:bg-gray-800 text-gray-300 hover:text-white px-3 py-2 rounded-lg text-sm transition-all"
            >
              <LogOut className="w-4 h-4" /> <span className="hidden sm:inline">Log Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Dashboard Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 mt-8 space-y-8">
        
        {/* Banner Welcome Message */}
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight">Hello, {user?.name}!</h2>
          <p className="text-gray-400 text-sm mt-1">Access and review all your structured interactive assets.</p>
        </div>

        {/* Aggregates Stats Widgets */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="glass-panel p-6 rounded-2xl flex items-center gap-4 border-white/5">
            <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20 text-blue-400">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_documents}</p>
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">Uploaded PDFs</p>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl flex items-center gap-4 border-white/5">
            <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center border border-purple-500/20 text-purple-400">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_flashcards}</p>
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">Generated Cards</p>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl flex items-center gap-4 border-white/5">
            <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center border border-amber-500/20 text-amber-400">
              <HelpCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total_quizzes}</p>
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">Created Quiz MCQs</p>
            </div>
          </div>
        </div>

        {/* Workspace Operations Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: PDF Uploader Area */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-panel p-6 rounded-2xl relative border-white/5">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                Upload New PDF <Sparkles className="w-4 h-4 text-indigo-400" />
              </h3>

              <div className="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all relative">
                <input 
                  type="file" 
                  accept=".pdf"
                  onChange={handleFileUpload}
                  disabled={uploadLoading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                {uploadLoading ? (
                  <div className="space-y-3">
                    <Loader className="w-10 h-10 text-indigo-400 animate-spin mx-auto" />
                    <p className="text-sm font-semibold">Uploading & parsing PDF...</p>
                    <p className="text-xs text-gray-400">This might take a moment.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="w-12 h-12 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto text-indigo-400">
                      <Upload className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">Click to upload document</p>
                      <p className="text-xs text-gray-400 mt-1">PDF format only. Size limit 100MB.</p>
                    </div>
                  </div>
                )}
              </div>

              {uploadError && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-300 rounded-lg text-xs">
                  {uploadError}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Uploaded Documents list */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-panel p-6 rounded-2xl border-white/5">
              <h3 className="font-bold text-lg mb-6">Your Documents Workspace</h3>
              
              {loading.docs && documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                  <Loader className="w-8 h-8 animate-spin mb-3 text-indigo-500" />
                  <p className="text-sm">Loading workspace sheets...</p>
                </div>
              ) : documents.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-gray-500 border border-dashed border-gray-800 rounded-2xl">
                  <FileText className="w-12 h-12 mb-3 text-gray-700" />
                  <p className="text-sm font-medium">No documents uploaded yet</p>
                  <p className="text-xs text-gray-600 mt-1">Upload a PDF to generate educational assets.</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-800/40">
                  {documents.map((doc) => (
                    <div 
                      key={doc.id}
                      className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4 group"
                    >
                      <div className="flex items-start gap-3 min-w-0">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center border shrink-0 ${
                          doc.status === 'ready' 
                            ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400' 
                            : doc.status === 'failed' 
                            ? 'bg-red-500/10 border-red-500/20 text-red-400' 
                            : 'bg-gray-500/10 border-gray-500/20 text-gray-400'
                        }`}>
                          {doc.status === 'ready' ? (
                            <FileText className="w-5 h-5" />
                          ) : doc.status === 'failed' ? (
                            <XCircle className="w-5 h-5" />
                          ) : (
                            <Loader className="w-5 h-5 animate-spin" />
                          )}
                        </div>

                        <div className="min-w-0">
                          {doc.status === 'ready' ? (
                            <Link 
                              to={`/document/${doc.id}`}
                              className="font-bold text-sm text-gray-100 hover:text-indigo-400 truncate block transition-all"
                            >
                              {doc.title}
                            </Link>
                          ) : (
                            <span className="font-bold text-sm text-gray-400 block truncate cursor-not-allowed">
                              {doc.title}
                            </span>
                          )}
                          
                          <div className="flex items-center gap-3 text-xs text-gray-500 mt-1 flex-wrap">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              {new Date(doc.created_at).toLocaleDateString()}
                            </span>
                            {doc.total_pages && (
                              <span>• {doc.total_pages} Pages</span>
                            )}
                            <span>• Status: {
                              doc.status === 'ready' ? (
                                <span className="text-emerald-400 font-semibold">Ready</span>
                              ) : doc.status === 'failed' ? (
                                <span className="text-red-400 font-semibold">Failed</span>
                              ) : (
                                <span className="text-indigo-400 font-semibold">Processing...</span>
                              )
                            }</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {doc.status === 'ready' && (
                          <Link 
                            to={`/document/${doc.id}`}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs px-3.5 py-2 rounded-lg transition-all"
                          >
                            Open Workspace
                          </Link>
                        )}
                        <button 
                          onClick={(e) => handleDelete(doc.id, e)}
                          className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                          title="Delete PDF and related items"
                        >
                          <Trash2 className="w-4.5 h-4.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}

export default DashboardPage;
