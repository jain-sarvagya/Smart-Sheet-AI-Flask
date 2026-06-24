// frontend/src/pages/LandingPage.jsx
/**
 * Purpose: Public Hero Landing Page.
 * Responsibilities:
 * - Wow the user with stunning royal-blue/purple glowing gradient aesthetics.
 * - Introduce key learning assets (quizzes, flashcards, chat, summaries).
 * - Direct users to Auth dashboard panel.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { 
  Sparkles, 
  FileText, 
  Brain, 
  MessageSquare, 
  ArrowRight, 
  Layers, 
  HelpCircle 
} from 'lucide-react';

function LandingPage() {
  const { isAuthenticated } = useSelector((state) => state.auth);

  return (
    <div className="relative overflow-hidden min-h-screen flex flex-col grid-bg">
      {/* Decorative Blur Orbs */}
      <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none" />

      {/* Header / Navbar */}
      <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-indigo-500 to-purple-600 p-2 rounded-xl shadow-glow-primary">
            <Layers className="w-6 h-6 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Smart-Sheet <span className="text-indigo-400">AI</span>
          </span>
        </div>
        <div>
          <Link 
            to={isAuthenticated ? "/dashboard" : "/auth"} 
            className="glass-panel px-5 py-2 rounded-lg text-sm font-semibold hover:border-indigo-500/40 hover:text-indigo-300 transition-all"
          >
            {isAuthenticated ? "Go to Dashboard" : "Sign In"}
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-6 flex flex-col items-center justify-center text-center z-10 py-16">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel border-indigo-500/20 mb-6 text-xs text-indigo-300 font-medium">
          <Sparkles className="w-3.5 h-3.5" /> Introducing Smart-Sheet AI (Flask Edition)
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.1] mb-6">
          Convert Static PDFs Into <br />
          <span className="shimmer-text">Interactive Study Assets</span>
        </h1>
        
        <p className="text-gray-400 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed">
          Upload your documents, and let Gemini-powered AI generate grounded quizzes, flashcards, detailed summaries, and interactive RAG chats—drawing strictly from your files.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-20">
          <Link 
            to={isAuthenticated ? "/dashboard" : "/auth"} 
            className="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold px-8 py-4 rounded-xl shadow-glow-primary hover:shadow-glow-secondary transform hover:-translate-y-0.5 transition-all"
          >
            Get Started Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full text-left">
          
          {/* Card 1: Summaries */}
          <div className="glass-panel-interactive p-6 rounded-2xl">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20 mb-4 text-blue-400">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Instant Summaries</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Generate structured, nested summaries and bulleted key takeaways from raw PDF text segments.
            </p>
          </div>

          {/* Card 2: Flashcards */}
          <div className="glass-panel-interactive p-6 rounded-2xl">
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20 mb-4 text-purple-400">
              <Brain className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Active Recall Cards</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Create quiz-style flashcard decks divided by easy, medium, and hard difficulties with flipped flip animations.
            </p>
          </div>

          {/* Card 3: Grounded Chat */}
          <div className="glass-panel-interactive p-6 rounded-2xl">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 mb-4 text-emerald-400">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Grounded AI Chat</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Inquire details from your document context. The bot will refuse to answer using external hallucinated knowledge.
            </p>
          </div>

          {/* Card 4: Quizzes */}
          <div className="glass-panel-interactive p-6 rounded-2xl">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center border border-amber-500/20 mb-4 text-amber-400">
              <HelpCircle className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg mb-2">Targeted Quizzes</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Auto-generate multiple-choice questionnaires featuring prompt feedback, correct answers, and AI explanations.
            </p>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800/40 w-full py-8 text-center text-xs text-gray-500 z-10 mt-16">
        © 2026 Smart-Sheet AI. All rights reserved. Powered by Google Gemini.
      </footer>
    </div>
  );
}

export default LandingPage;
