// frontend/src/pages/DocumentStudioPage.jsx
/**
 * Purpose: Document workspace page showing PDF side-by-side with AI generation tools.
 * Responsibilities:
 * - Render side-by-side layout: PDF iframe on the left, tabbed AI workspace on the right.
 * - Poll document details to ensure it is loaded.
 * - Tab 1: Summary Studio - trigger generation and view narrative details.
 * - Tab 2: Flashcard Studio - active recall deck with 3D card flips and difficulty filters.
 * - Tab 3: Quiz Arena - interactive multiple choice questions with feedback and explanations.
 * - Tab 4: Chat Space - document-grounded RAG chatbot dialog.
 * - Tab 5: Concept Solver - solve definitions from the document text.
 */

import React, { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchDocumentById,
  generateSummary,
  fetchSummary,
  generateFlashcards,
  fetchFlashcards,
  generateQuizzes,
  fetchQuizzes,
  explainConcept,
  fetchExplanations,
  fetchChatHistory,
  sendChatMessage,
  appendUserMessage,
  clearCurrentDocument,
  clearQuizzes,
  clearError
} from '../redux/slices/docSlice';
import { 
  ArrowLeft, 
  FileText, 
  Brain, 
  HelpCircle, 
  MessageSquare, 
  BookOpen, 
  Sparkles, 
  Loader, 
  ChevronLeft, 
  ChevronRight,
  Send,
  Plus,
  Award,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Play
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function DocumentStudioPage() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const messagesEndRef = useRef(null);

  const { 
    currentDocument, 
    summary, 
    flashcards, 
    quizzes, 
    explanations, 
    chatHistory, 
    loading,
    error
  } = useSelector((state) => state.docs);

  const [activeTab, setActiveTab] = useState('summary');
  
  // Flashcards state
  const [currentCardIdx, setCurrentCardIdx] = useState(0);
  const [isCardFlipped, setIsCardFlipped] = useState(false);
  const [cardFilter, setCardFilter] = useState('All');

  // Quiz state
  const [selectedAnswers, setSelectedAnswers] = useState({}); // { quizId: selectedOption }
  const [resetQuizKey, setResetQuizKey] = useState(0); // force refresh
  const [quizCount, setQuizCount] = useState(5);
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  // Concept state
  const [newConcept, setNewConcept] = useState('');

  // Chat state
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    dispatch(fetchDocumentById(id));
    dispatch(fetchSummary(id));
    dispatch(fetchFlashcards(id));
    dispatch(fetchQuizzes(id));
    dispatch(fetchExplanations(id));
    dispatch(fetchChatHistory(id));

    return () => {
      dispatch(clearCurrentDocument());
    };
  }, [dispatch, id]);

  // Scroll chat window to bottom when history changes
  useEffect(() => {
    if (activeTab === 'chat') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, activeTab]);

  if (!currentDocument) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-gray-500">
        <Loader className="w-10 h-10 text-indigo-500 animate-spin mb-3" />
        <p className="text-sm">Loading document workspace...</p>
      </div>
    );
  }

  // Format PDF URL if local fallback is used
  const getPdfUrl = (url) => {
    if (url.startsWith('/api/')) {
      return `http://localhost:5000${url}`;
    }
    return url;
  };

  // Helper trigger hooks
  const handleGenerateSummary = () => dispatch(generateSummary(id));
  const handleGenerateFlashcards = () => {
    dispatch(generateFlashcards(id));
    setCurrentCardIdx(0);
    setIsCardFlipped(false);
  };
  const handleGenerateQuizzes = (countVal = 5) => {
    dispatch(generateQuizzes({ docId: id, count: countVal }));
    setSelectedAnswers({});
    setQuizSubmitted(false);
    setResetQuizKey(prev => prev + 1);
  };

  const handleConceptSubmit = (e) => {
    e.preventDefault();
    if (!newConcept.trim()) return;
    dispatch(explainConcept({ docId: id, conceptName: newConcept.trim() }));
    setNewConcept('');
  };

  const handleSendChat = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const query = chatInput.trim();
    setChatInput('');
    
    // Optimistically push user message to history
    dispatch(appendUserMessage(query));
    // Trigger API call
    dispatch(sendChatMessage({ docId: id, message: query }));
  };

  // Filters cards based on difficulty
  const filteredCards = cardFilter === 'All' 
    ? flashcards 
    : flashcards.filter(c => c.difficulty === cardFilter);

  const handleCardNext = () => {
    setIsCardFlipped(false);
    setTimeout(() => {
      setCurrentCardIdx((prev) => (prev + 1) % filteredCards.length);
    }, 150);
  };

  const handleCardPrev = () => {
    setIsCardFlipped(false);
    setTimeout(() => {
      setCurrentCardIdx((prev) => (prev - 1 + filteredCards.length) % filteredCards.length);
    }, 150);
  };

  const handleSelectOption = (quizId, option) => {
    if (quizSubmitted) return; // cannot change after submission
    setSelectedAnswers({ ...selectedAnswers, [quizId]: option });
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f19]">
      
      {/* Workspace Header */}
      <header className="border-b border-gray-800 bg-gray-950/65 backdrop-blur-md px-6 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4 min-w-0">
          <Link 
            to="/dashboard" 
            className="p-2 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-all"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="min-w-0">
            <h2 className="font-extrabold text-sm sm:text-base text-gray-100 truncate">{currentDocument.title}</h2>
            <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
              <span>PDF Studio</span> • <span>{currentDocument.total_pages || '?'} Pages</span>
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-full">
            ● Document Active
          </span>
        </div>
      </header>

      {/* Main Split Layout */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        {/* Left Side: PDF Reader Preview Panel */}
        <div className="w-full md:w-[48%] lg:w-[50%] p-4 border-r border-gray-800/80 flex flex-col bg-gray-950/40">
          <iframe 
            src={getPdfUrl(currentDocument.file_url)} 
            className="w-full flex-1 rounded-xl bg-gray-900 border border-gray-800/80 shadow-2xl"
            title="PDF Document Viewer"
          />
        </div>

        {/* Right Side: Tabbed AI Studio Workspace Panel */}
        <div className="w-full md:w-[52%] lg:w-[50%] flex flex-col bg-gray-950/20">
          
          {/* Tab Selector Buttons */}
          <div className="flex border-b border-gray-800/80 bg-gray-950/40 shrink-0 overflow-x-auto">
            <button 
              onClick={() => setActiveTab('summary')}
              className={`flex-1 py-4 px-3 flex items-center justify-center gap-2 border-b-2 text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === 'summary' 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/30'
              }`}
            >
              <FileText className="w-4 h-4" /> Summary
            </button>
            <button 
              onClick={() => setActiveTab('flashcards')}
              className={`flex-1 py-4 px-3 flex items-center justify-center gap-2 border-b-2 text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === 'flashcards' 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/30'
              }`}
            >
              <Brain className="w-4 h-4" /> Flashcards
            </button>
            <button 
              onClick={() => setActiveTab('quiz')}
              className={`flex-1 py-4 px-3 flex items-center justify-center gap-2 border-b-2 text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === 'quiz' 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/30'
              }`}
            >
              <HelpCircle className="w-4 h-4" /> Quiz
            </button>
            <button 
              onClick={() => setActiveTab('chat')}
              className={`flex-1 py-4 px-3 flex items-center justify-center gap-2 border-b-2 text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === 'chat' 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/30'
              }`}
            >
              <MessageSquare className="w-4 h-4" /> Chat
            </button>
            <button 
              onClick={() => setActiveTab('explain')}
              className={`flex-1 py-4 px-3 flex items-center justify-center gap-2 border-b-2 text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === 'explain' 
                  ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5' 
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/30'
              }`}
            >
              <BookOpen className="w-4 h-4" /> Concept
            </button>
          </div>

          {/* Active Tab panel contents */}
          <div className="flex-1 overflow-y-auto p-6">
            {error && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs sm:text-sm flex items-center justify-between animate-fade-in shadow-glow-error">
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 shrink-0 text-red-400" />
                  <span>{error}</span>
                </div>
                <button 
                  onClick={() => dispatch(clearError())}
                  className="text-red-400 hover:text-red-300 font-bold ml-4 text-xs tracking-wider uppercase shrink-0"
                >
                  Dismiss
                </button>
              </div>
            )}
            
            {/* T1: Summary tab */}
            {activeTab === 'summary' && (
              <div className="space-y-6">
                {!summary ? (
                  <div className="text-center py-16">
                    <div className="w-16 h-16 bg-indigo-500/10 rounded-2xl flex items-center justify-center border border-indigo-500/20 mx-auto text-indigo-400 mb-4 shadow-glow-primary">
                      <FileText className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-bold mb-2">Generate PDF Summary</h3>
                    <p className="text-sm text-gray-400 max-w-md mx-auto mb-6">
                      Analyze the document text and extract narrative summaries, structured deep dives, and key takeaways.
                    </p>
                    <button 
                      onClick={handleGenerateSummary}
                      disabled={loading.summary}
                      className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-xl inline-flex items-center gap-2 transition-all shadow-glow-primary"
                    >
                      {loading.summary ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" /> Generating Summary...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5" /> Generate Summary
                        </>
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="space-y-6 animate-fade-in">
                    
                    {/* Short Summary */}
                    <div className="glass-panel p-5 rounded-xl border-white/5">
                      <h4 className="text-xs uppercase font-semibold tracking-wider text-indigo-400 mb-2">Overview</h4>
                      <p className="text-sm text-gray-200 leading-relaxed font-medium">{summary.short_summary}</p>
                    </div>

                    {/* Detailed Summary */}
                    <div className="glass-panel p-5 rounded-xl border-white/5">
                      <h4 className="text-xs uppercase font-semibold tracking-wider text-indigo-400 mb-2">Detailed Deep Dive</h4>
                      <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">{summary.detailed_summary}</p>
                    </div>

                    {/* Key Takeaways */}
                    <div className="glass-panel p-5 rounded-xl border-white/5">
                      <h4 className="text-xs uppercase font-semibold tracking-wider text-indigo-400 mb-3">Key Takeaways</h4>
                      <ul className="space-y-2">
                        {summary.key_takeaways.map((takeaway, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex items-start gap-2.5">
                            <span className="text-indigo-400 mt-1 shrink-0">•</span>
                            <span>{takeaway}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                  </div>
                )}
              </div>
            )}

            {/* T2: Flashcards tab */}
            {activeTab === 'flashcards' && (
              <div className="space-y-6">
                {flashcards.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="w-16 h-16 bg-purple-500/10 rounded-2xl flex items-center justify-center border border-purple-500/20 mx-auto text-purple-400 mb-4 shadow-glow-secondary">
                      <Brain className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-bold mb-2">Generate Active Recall Cards</h3>
                    <p className="text-sm text-gray-400 max-w-md mx-auto mb-6">
                      Create a deck of interactive, flip-on-click flashcards covering vital document concepts.
                    </p>
                    <button 
                      onClick={handleGenerateFlashcards}
                      disabled={loading.flashcards}
                      className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-xl inline-flex items-center gap-2 transition-all shadow-glow-primary"
                    >
                      {loading.flashcards ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" /> Generating Cards...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5" /> Generate Flashcards
                        </>
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-6">
                    
                    {/* Filters & Actions */}
                    <div className="w-full flex items-center justify-between border-b border-gray-800 pb-4">
                      <div className="flex gap-2">
                        {['All', 'Easy', 'Medium', 'Hard'].map((diff) => (
                          <button
                            key={diff}
                            onClick={() => {
                              setCardFilter(diff);
                              setCurrentCardIdx(0);
                            }}
                            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                              cardFilter === diff 
                                ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' 
                                : 'text-gray-400 hover:text-gray-200'
                            }`}
                          >
                            {diff}
                          </button>
                        ))}
                      </div>
                      <span className="text-xs text-gray-500">
                        {filteredCards.length > 0 ? `${currentCardIdx + 1} / ${filteredCards.length}` : '0 Cards'}
                      </span>
                    </div>

                    {filteredCards.length === 0 ? (
                      <div className="py-12 text-center text-gray-500 text-sm">
                        No flashcards found matching the selected difficulty filter.
                      </div>
                    ) : (
                      <>
                        {/* Interactive Flip Card Card */}
                        <div 
                          className="perspective-1000 w-full max-w-md h-64 cursor-pointer"
                          onClick={() => setIsCardFlipped(!isCardFlipped)}
                        >
                          <div className={`relative w-full h-full duration-500 transform-style-3d transition-transform ${
                            isCardFlipped ? 'rotate-y-180' : ''
                          }`}>
                            {/* Front Panel */}
                            <div className="absolute inset-0 backface-hidden glass-panel flex flex-col justify-between p-6 rounded-2xl border-white/10 select-none bg-gray-900/80">
                              <div className="flex justify-between items-center shrink-0">
                                <span className="text-xs uppercase text-indigo-400 tracking-wider font-semibold">Question</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  filteredCards[currentCardIdx].difficulty === 'Easy' 
                                    ? 'bg-emerald-500/10 text-emerald-400' 
                                    : filteredCards[currentCardIdx].difficulty === 'Hard' 
                                    ? 'bg-red-500/10 text-red-400' 
                                    : 'bg-amber-500/10 text-amber-400'
                                }`}>
                                  {filteredCards[currentCardIdx].difficulty}
                                </span>
                              </div>
                              
                              <p className="text-center font-bold text-base sm:text-lg leading-relaxed flex-1 flex items-center justify-center">
                                {filteredCards[currentCardIdx].question}
                              </p>
                              
                              <span className="text-[10px] text-gray-500 text-center uppercase tracking-widest shrink-0 mt-2">
                                Click to Flip Card
                              </span>
                            </div>

                            {/* Back Panel */}
                            <div className="absolute inset-0 backface-hidden rotate-y-180 bg-gradient-to-tr from-indigo-950 to-indigo-900/90 border border-indigo-500/30 flex flex-col justify-between p-6 rounded-2xl select-none">
                              <span className="text-xs uppercase text-emerald-400 tracking-wider font-semibold shrink-0">Answer Summary</span>
                              
                              <p className="text-center font-bold text-sm sm:text-base leading-relaxed flex-1 flex items-center justify-center text-gray-200">
                                {filteredCards[currentCardIdx].answer}
                              </p>
                              
                              <span className="text-[10px] text-gray-500 text-center uppercase tracking-widest shrink-0 mt-2">
                                Click to Flip Back
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Navigation Arrows */}
                        <div className="flex items-center gap-6 mt-2">
                          <button
                            onClick={handleCardPrev}
                            className="p-3 bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-full transition-all text-gray-400 hover:text-white"
                          >
                            <ChevronLeft className="w-5 h-5" />
                          </button>
                          <button
                            onClick={handleCardNext}
                            className="p-3 bg-gray-900 hover:bg-gray-800 border border-gray-800 rounded-full transition-all text-gray-400 hover:text-white"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </button>
                        </div>
                      </>
                    )}

                    {/* Reset Deck Button */}
                    <button
                      onClick={handleGenerateFlashcards}
                      disabled={loading.flashcards}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold hover:underline mt-4"
                    >
                      Regenerate Flashcards Deck
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* T3: Quiz Arena tab */}
            {activeTab === 'quiz' && (
              <div className="space-y-6">
                {quizzes.length === 0 ? (
                  /* SETUP VIEW */
                  <div className="text-center py-12 max-w-md mx-auto animate-fade-in">
                    <div className="w-16 h-16 bg-amber-500/10 rounded-2xl flex items-center justify-center border border-amber-500/20 mx-auto text-amber-400 mb-4 shadow-glow-primary">
                      <HelpCircle className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-extrabold mb-2 text-white">Generate Practice Quiz</h3>
                    <p className="text-sm text-gray-400 mb-6 font-medium">
                      Customize a multiple-choice quiz covering concepts in this document to test your knowledge.
                    </p>

                    <div className="glass-panel p-5 rounded-2xl border-white/5 mb-6 text-left bg-gray-900/40">
                      <label className="block text-xs uppercase tracking-wider font-semibold text-indigo-400 mb-3">
                        Number of Questions
                      </label>
                      <div className="grid grid-cols-4 gap-2">
                        {[3, 5, 10, 15].map((num) => (
                          <button
                            key={num}
                            type="button"
                            onClick={() => setQuizCount(num)}
                            className={`py-2 rounded-xl text-sm font-bold border transition-all ${
                              quizCount === num
                                ? 'bg-indigo-600 text-white border-indigo-500 shadow-glow-primary'
                                : 'bg-gray-900 border-gray-800 text-gray-400 hover:text-white hover:bg-gray-800'
                            }`}
                          >
                            {num}
                          </button>
                        ))}
                      </div>
                    </div>

                    <button 
                      onClick={() => handleGenerateQuizzes(quizCount)}
                      disabled={loading.quizzes}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold py-3.5 rounded-xl inline-flex items-center justify-center gap-2 transition-all shadow-glow-primary"
                    >
                      {loading.quizzes ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" /> Generating Quiz...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-5 h-5" /> Build Quiz
                        </>
                      )}
                    </button>
                  </div>
                ) : !quizSubmitted ? (
                  /* ACTIVE QUIZ VIEW */
                  <div key={resetQuizKey} className="space-y-6 animate-fade-in pb-12">
                    <div className="glass-panel p-4 rounded-xl border-white/5 flex items-center justify-between bg-indigo-950/20">
                      <div>
                        <h4 className="font-bold text-sm text-gray-100">Practice Quiz</h4>
                        <p className="text-xs text-gray-400 mt-0.5 font-medium">
                          Answer the questions below, then click submit to view results.
                        </p>
                      </div>
                      <span className="px-2.5 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold rounded-lg whitespace-nowrap">
                        {Object.keys(selectedAnswers).length} of {quizzes.length} Answered
                      </span>
                    </div>

                    {quizzes.map((quiz, qIdx) => {
                      const selected = selectedAnswers[quiz.id];
                      return (
                        <div key={quiz.id} className="glass-panel p-6 rounded-2xl border-white/5 bg-gray-900/30">
                          <div className="flex items-start gap-3">
                            <span className="flex items-center justify-center w-6 h-6 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-bold rounded-lg shrink-0 mt-0.5">
                              {qIdx + 1}
                            </span>
                            <h4 className="font-bold text-sm sm:text-base leading-relaxed text-gray-200">{quiz.question}</h4>
                          </div>

                          <div className="grid grid-cols-1 gap-3 mt-5">
                            {['A', 'B', 'C', 'D'].map((opt) => {
                              const optionText = quiz[`option_${opt.toLowerCase()}`];
                              const isOptionSelected = selected === opt;
                              const buttonStyles = isOptionSelected
                                ? "border-indigo-500 bg-indigo-500/10 text-indigo-300 shadow-glow-primary"
                                : "border-gray-800 text-gray-300 hover:bg-gray-850 hover:border-gray-700";

                              return (
                                <button
                                  key={opt}
                                  onClick={() => handleSelectOption(quiz.id, opt)}
                                  className={`w-full text-left border rounded-xl px-4 py-3 text-xs sm:text-sm font-medium flex items-center gap-3 transition-all ${buttonStyles}`}
                                >
                                  <span className={`w-5 h-5 flex items-center justify-center rounded border text-xs font-bold ${
                                    isOptionSelected 
                                      ? 'border-indigo-400 text-indigo-400 bg-indigo-500/5' 
                                      : 'border-gray-700 text-gray-400'
                                  }`}>
                                    {opt}
                                  </span>
                                  <span>{optionText}</span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      );
                    })}

                    <div className="flex flex-col gap-3 mt-8">
                      <button
                        onClick={() => setQuizSubmitted(true)}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 rounded-xl transition-all shadow-glow-primary text-sm flex items-center justify-center gap-2"
                      >
                        <Play className="w-4 h-4 fill-white" /> Submit Quiz
                      </button>
                      <button
                        onClick={() => {
                          dispatch(clearQuizzes());
                          setSelectedAnswers({});
                          setQuizSubmitted(false);
                        }}
                        className="text-xs text-gray-400 hover:text-gray-300 font-semibold hover:underline text-center mt-1"
                      >
                        Cancel & Create New Quiz
                      </button>
                    </div>
                  </div>
                ) : (
                  /* ANALYSIS DASHBOARD VIEW */
                  <div key={resetQuizKey} className="space-y-6 animate-fade-in pb-12">
                    {(() => {
                      const correctCount = quizzes.filter(q => selectedAnswers[q.id] === q.correct_answer).length;
                      const percentage = Math.round((correctCount / quizzes.length) * 100);
                      
                      let badgeColor = "bg-red-500/10 border-red-500/20 text-red-400";
                      let badgeText = "Reviewer";
                      let commentText = "Needs review. We recommend reading through the summaries and asking Gemini questions in the chat space.";
                      let ringColor = "text-red-500 border-red-500/20";
                      
                      if (percentage >= 80) {
                        badgeColor = "bg-emerald-500/10 border-emerald-500/20 text-emerald-400";
                        badgeText = "🏆 Mastermind";
                        commentText = "Outstanding work! You have a thorough grasp of the materials in this document.";
                        ringColor = "text-emerald-500 border-emerald-500/20";
                      } else if (percentage >= 50) {
                        badgeColor = "bg-amber-500/10 border-amber-500/20 text-amber-400";
                        badgeText = "📚 Scholar";
                        commentText = "Good effort! Go through the incorrect items below to secure a perfect score next time.";
                        ringColor = "text-amber-500 border-amber-500/20";
                      }

                      return (
                        <>
                          {/* Result Dashboard Card */}
                          <div className="glass-panel p-6 rounded-2xl border-white/5 bg-gradient-to-br from-indigo-950/20 to-gray-900/40 relative overflow-hidden flex flex-col sm:flex-row items-center gap-6">
                            
                            {/* Score Ring */}
                            <div className={`relative shrink-0 flex items-center justify-center w-24 h-24 rounded-full border-4 bg-gray-950/40 ${ringColor}`}>
                              <div className="text-center">
                                <span className="text-2xl font-black">{percentage}%</span>
                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Score</p>
                              </div>
                            </div>

                            {/* Score Performance Details */}
                            <div className="flex-1 text-center sm:text-left">
                              <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2 justify-center sm:justify-start">
                                <h4 className="font-extrabold text-lg text-white">Quiz Completed</h4>
                                <span className={`px-2.5 py-0.5 border text-xs font-black rounded-lg w-fit mx-auto sm:mx-0 ${badgeColor}`}>
                                  {badgeText}
                                </span>
                              </div>
                              <p className="text-xs text-gray-400 leading-relaxed font-medium">
                                {commentText}
                              </p>
                              <div className="mt-3 text-xs text-indigo-400 font-bold">
                                You got {correctCount} out of {quizzes.length} questions correct.
                              </div>
                            </div>
                          </div>

                          {/* Analysis list review */}
                          <h4 className="font-bold text-xs uppercase tracking-wider text-gray-400 mt-6 mb-2">Pedagogical Review</h4>
                          
                          {quizzes.map((quiz, qIdx) => {
                            const selected = selectedAnswers[quiz.id];
                            const isCorrect = selected === quiz.correct_answer;
                            
                            return (
                              <div key={quiz.id} className="glass-panel p-6 rounded-2xl border-white/5 relative bg-gray-900/30">
                                
                                <div className="flex items-start gap-3">
                                  {isCorrect ? (
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                                  ) : (
                                    <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                                  )}
                                  <div>
                                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Question {qIdx + 1}</span>
                                    <h4 className="font-bold text-sm sm:text-base leading-relaxed text-gray-200 mt-0.5">{quiz.question}</h4>
                                  </div>
                                </div>

                                <div className="grid grid-cols-1 gap-3 mt-5">
                                  {['A', 'B', 'C', 'D'].map((opt) => {
                                    const optionText = quiz[`option_${opt.toLowerCase()}`];
                                    const isOptionSelected = selected === opt;
                                    const isOptionCorrect = quiz.correct_answer === opt;
                                    
                                    let buttonStyles = "border-gray-800 text-gray-500 opacity-60";
                                    if (isOptionCorrect) {
                                      buttonStyles = "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 opacity-100 font-bold";
                                    } else if (isOptionSelected) {
                                      buttonStyles = "border-red-500/40 bg-red-500/10 text-red-300 opacity-100 font-bold";
                                    }

                                    return (
                                      <div
                                        key={opt}
                                        className={`w-full text-left border rounded-xl px-4 py-3 text-xs sm:text-sm flex items-center gap-3 transition-all ${buttonStyles}`}
                                      >
                                        <span className={`w-5 h-5 flex items-center justify-center rounded border text-xs font-bold ${
                                          isOptionSelected 
                                            ? 'border-indigo-400 text-indigo-400 bg-indigo-500/5' 
                                            : 'border-gray-700 text-gray-400'
                                        }`}>
                                          {opt}
                                        </span>
                                        <span>{optionText}</span>
                                      </div>
                                    );
                                  })}
                                </div>

                                <div className="mt-4 p-4 bg-gray-900/60 border border-gray-800/80 rounded-xl">
                                  <p className={`text-xs font-bold uppercase tracking-wider mb-1.5 ${
                                    isCorrect ? 'text-emerald-400' : 'text-red-400'
                                  }`}>
                                    {isCorrect ? "✓ Answer Correct" : `✗ Answer Incorrect (Correct Option: ${quiz.correct_answer})`}
                                  </p>
                                  <p className="text-xs sm:text-sm text-gray-400 leading-relaxed whitespace-pre-line font-medium">
                                    {quiz.explanation}
                                  </p>
                                </div>

                              </div>
                            );
                          })}

                          {/* Action footer */}
                          <div className="flex flex-col sm:flex-row gap-3 mt-8">
                            <button
                              onClick={() => {
                                setSelectedAnswers({});
                                setQuizSubmitted(false);
                                setResetQuizKey(prev => prev + 1);
                              }}
                              className="flex-1 bg-gray-900 hover:bg-gray-850 text-white font-bold py-3 px-5 border border-gray-800 rounded-xl transition-all flex items-center justify-center gap-2"
                            >
                              <RefreshCw className="w-4 h-4 text-indigo-400" /> Retake This Quiz
                            </button>
                            <button
                              onClick={() => {
                                dispatch(clearQuizzes());
                                setSelectedAnswers({});
                                setQuizSubmitted(false);
                              }}
                              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-5 rounded-xl transition-all shadow-glow-primary flex items-center justify-center gap-2"
                            >
                              <Plus className="w-4 h-4 text-white" /> Create New Quiz
                            </button>
                          </div>
                        </>
                      );
                    })()}
                  </div>
                )}
              </div>
            )}

            {/* T4: Grounded AI Chat tab */}
            {activeTab === 'chat' && (
              <div className="flex flex-col h-[calc(100vh-220px)] relative">
                
                {/* Scrollable messages dialog */}
                <div className="flex-1 overflow-y-auto space-y-4 pr-2 pb-6">
                  {chatHistory.length === 0 ? (
                    <div className="text-center py-16 flex flex-col items-center justify-center">
                      <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center border border-emerald-500/20 text-emerald-400 mb-4 shadow-glow-primary">
                        <MessageSquare className="w-8 h-8" />
                      </div>
                      <h3 className="text-lg font-bold mb-2">Document Grounded RAG Chat</h3>
                      <p className="text-sm text-gray-400 max-w-sm mx-auto">
                        Ask any questions regarding the PDF. Answers are strictly verified against matching context fragments.
                      </p>
                    </div>
                  ) : (
                    chatHistory.map((msg) => {
                      const isUser = msg.sender === 'user';
                      return (
                        <div 
                          key={msg.id}
                          className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
                        >
                          <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed shadow-lg ${
                            isUser 
                              ? 'bg-indigo-600 text-white rounded-br-none' 
                              : 'bg-gray-900 border border-gray-800 text-gray-200 rounded-bl-none'
                          }`}>
                            <p className="whitespace-pre-line">{msg.message}</p>
                            
                            {/* Citations alert tag on Assistant answers */}
                            {!isUser && msg.message !== "The uploaded document does not contain enough information to answer this question." && (
                              <span className="inline-flex items-center gap-1 text-[9px] text-indigo-400 font-bold uppercase tracking-wider mt-2">
                                ✓ Verified Grounded Context
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                  
                  {loading.chat && (
                    <div className="flex justify-start animate-pulse">
                      <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-2 text-xs text-gray-500">
                        <Loader className="w-4 h-4 animate-spin text-indigo-500" /> Grounding context & answering...
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Bottom Input Area */}
                <form 
                  onSubmit={handleSendChat}
                  className="border-t border-gray-800 bg-gray-950/60 p-4 absolute bottom-0 left-0 right-0 flex gap-2 shrink-0 rounded-xl"
                >
                  <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={loading.chat}
                    placeholder="Ask a question about the document..."
                    className="flex-1 bg-gray-900 border border-gray-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs sm:text-sm focus:outline-none transition-all"
                  />
                  <button 
                    type="submit"
                    disabled={loading.chat || !chatInput.trim()}
                    className="p-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-xl transition-all shadow-glow-primary shrink-0"
                  >
                    <Send className="w-4 h-4 sm:w-5 h-5" />
                  </button>
                </form>

              </div>
            )}

            {/* T5: Concept explanations tab */}
            {activeTab === 'explain' && (
              <div className="space-y-6">
                
                {/* Solver query form */}
                <div className="glass-panel p-5 rounded-2xl border-white/5 bg-gray-900/30">
                  <h4 className="font-bold text-sm sm:text-base mb-3 flex items-center gap-2">
                    Explain a Concept <BookOpen className="w-4 h-4 text-indigo-400" />
                  </h4>
                  <p className="text-xs text-gray-400 mb-4 leading-relaxed">
                    Type a complex term or concept. Gemini will scour the PDF and generate a grounded, markdown-formatted definition.
                  </p>
                  
                  <form onSubmit={handleConceptSubmit} className="flex gap-2">
                    <input 
                      type="text" 
                      value={newConcept}
                      onChange={(e) => setNewConcept(e.target.value)}
                      placeholder="e.g. Backpropagation, Cellular Mitosis..."
                      className="flex-1 bg-gray-950 border border-gray-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs sm:text-sm focus:outline-none transition-all"
                    />
                    <button 
                      type="submit"
                      disabled={loading.explain || !newConcept.trim()}
                      className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs sm:text-sm font-semibold transition-all shadow-glow-primary flex items-center gap-1"
                    >
                      {loading.explain ? (
                        <Loader className="w-4 h-4 animate-spin" />
                      ) : (
                        <Plus className="w-4 h-4" />
                      )}
                      <span>Explain</span>
                    </button>
                  </form>
                </div>

                {/* Explanation History List */}
                <div className="space-y-4">
                  <h4 className="font-bold text-xs uppercase tracking-wider text-gray-400">Past Concepts Explained</h4>
                  
                  {explanations.length === 0 ? (
                    <div className="text-center py-8 text-gray-500 text-xs border border-dashed border-gray-800 rounded-xl">
                      No concepts explained yet. Enter one above!
                    </div>
                  ) : (
                    explanations.map((exp) => (
                      <div key={exp.id} className="glass-panel p-5 rounded-2xl border-white/5 bg-gray-900/20">
                        <h5 className="font-bold text-sm text-indigo-400 mb-2 border-b border-gray-800/60 pb-1.5">{exp.concept_name}</h5>
                        <div className="text-xs sm:text-sm text-gray-300 leading-relaxed whitespace-pre-line markdown-body">
                          {exp.explanation}
                        </div>
                      </div>
                    ))
                  )}
                </div>

              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

export default DocumentStudioPage;
