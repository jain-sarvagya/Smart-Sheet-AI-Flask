// frontend/src/redux/slices/docSlice.js
/**
 * Purpose: Redux slice for managing Documents and associated learning assets.
 * Responsibilities:
 * - Handle document uploads, list fetches, and deletions.
 * - Manage document state (status check polling).
 * - Trigger and retrieve generated summaries, flashcards, quizzes, and explanations.
 * - Handle sending queries and receiving response streams from the RAG chatbot.
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

// Async Thunks
export const fetchDocuments = createAsyncThunk(
  'docs/fetchList',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/documents/`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to load documents');
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'docs/upload',
  async (formData, { rejectWithValue }) => {
    try {
      const headers = getHeaders();
      const response = await axios.post(`${API_URL}/documents/upload`, formData, {
        headers: {
          ...headers.headers,
          'Content-Type': 'multipart/form-data',
        }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to upload document');
    }
  }
);

export const deleteDocument = createAsyncThunk(
  'docs/delete',
  async (docId, { rejectWithValue }) => {
    try {
      await axios.delete(`${API_URL}/documents/${docId}`, getHeaders());
      return docId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete document');
    }
  }
);

export const fetchDocumentById = createAsyncThunk(
  'docs/fetchDetail',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/documents/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to get document details');
    }
  }
);

// Summaries
export const generateSummary = createAsyncThunk(
  'docs/generateSummary',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/summaries/generate/${docId}`, {}, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to generate summary');
    }
  }
);

export const fetchSummary = createAsyncThunk(
  'docs/fetchSummary',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/summaries/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Summary not found');
    }
  }
);

// Flashcards
export const generateFlashcards = createAsyncThunk(
  'docs/generateFlashcards',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/flashcards/generate/${docId}`, {}, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to generate flashcards');
    }
  }
);

export const fetchFlashcards = createAsyncThunk(
  'docs/fetchFlashcards',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/flashcards/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch flashcards');
    }
  }
);

// Quizzes
export const generateQuizzes = createAsyncThunk(
  'docs/generateQuizzes',
  async ({ docId, count }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/quizzes/generate/${docId}`, { count }, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to generate quizzes');
    }
  }
);

export const fetchQuizzes = createAsyncThunk(
  'docs/fetchQuizzes',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/quizzes/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch quizzes');
    }
  }
);

// Explanations
export const explainConcept = createAsyncThunk(
  'docs/explainConcept',
  async ({ docId, conceptName }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/explanations/explain/${docId}`, { concept_name: conceptName }, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to explain concept');
    }
  }
);

export const fetchExplanations = createAsyncThunk(
  'docs/fetchExplanations',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/explanations/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch explanation history');
    }
  }
);

// Chat (RAG)
export const fetchChatHistory = createAsyncThunk(
  'docs/fetchChatHistory',
  async (docId, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_URL}/chat/${docId}`, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch chat history');
    }
  }
);

export const sendChatMessage = createAsyncThunk(
  'docs/sendChatMessage',
  async ({ docId, message }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/chat/${docId}`, { message }, getHeaders());
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to send message');
    }
  }
);

const initialState = {
  documents: [],
  currentDocument: null,
  summary: null,
  flashcards: [],
  quizzes: [],
  explanations: [],
  chatHistory: [],
  loading: {
    docs: false,
    summary: false,
    flashcards: false,
    quizzes: false,
    explain: false,
    chat: false
  },
  error: null
};

const docSlice = createSlice({
  name: 'docs',
  initialState,
  reducers: {
    clearCurrentDocument: (state) => {
      state.currentDocument = null;
      state.summary = null;
      state.flashcards = [];
      state.quizzes = [];
      state.explanations = [];
      state.chatHistory = [];
      state.error = null;
    },
    clearQuizzes: (state) => {
      state.quizzes = [];
    },
    clearError: (state) => {
      state.error = null;
    },
    // Useful for optimistically pushing user chat bubble before thunk finishes
    appendUserMessage: (state, action) => {
      state.chatHistory.push({
        id: Date.now(),
        sender: 'user',
        message: action.payload,
        created_at: new Date().toISOString()
      });
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch list
      .addCase(fetchDocuments.pending, (state) => {
        state.loading.docs = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading.docs = false;
        state.documents = action.payload.documents;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading.docs = false;
        state.error = action.payload;
      })
      // Upload
      .addCase(uploadDocument.pending, (state) => {
        state.loading.docs = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.loading.docs = false;
        state.documents.unshift(action.payload.document);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading.docs = false;
        state.error = action.payload;
      })
      // Delete
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.documents = state.documents.filter(doc => doc.id !== action.payload);
        if (state.currentDocument?.id === action.payload) {
          state.currentDocument = null;
        }
      })
      // Fetch details / poll status
      .addCase(fetchDocumentById.fulfilled, (state, action) => {
        state.currentDocument = action.payload.document;
        // update it in list as well
        const idx = state.documents.findIndex(d => d.id === action.payload.document.id);
        if (idx !== -1) {
          state.documents[idx] = action.payload.document;
        }
      })
      // Summary generate
      .addCase(generateSummary.pending, (state) => {
        state.loading.summary = true;
        state.error = null;
      })
      .addCase(generateSummary.fulfilled, (state, action) => {
        state.loading.summary = false;
        state.summary = action.payload.summary;
      })
      .addCase(generateSummary.rejected, (state, action) => {
        state.loading.summary = false;
        state.error = action.payload;
      })
      // Summary fetch
      .addCase(fetchSummary.fulfilled, (state, action) => {
        state.summary = action.payload.summary;
      })
      .addCase(fetchSummary.rejected, (state) => {
        state.summary = null;
      })
      // Flashcards generate
      .addCase(generateFlashcards.pending, (state) => {
        state.loading.flashcards = true;
        state.error = null;
      })
      .addCase(generateFlashcards.fulfilled, (state, action) => {
        state.loading.flashcards = false;
        state.flashcards = action.payload.flashcards;
      })
      .addCase(generateFlashcards.rejected, (state, action) => {
        state.loading.flashcards = false;
        state.error = action.payload;
      })
      // Flashcards fetch
      .addCase(fetchFlashcards.fulfilled, (state, action) => {
        state.flashcards = action.payload.flashcards;
      })
      // Quizzes generate
      .addCase(generateQuizzes.pending, (state) => {
        state.loading.quizzes = true;
        state.error = null;
      })
      .addCase(generateQuizzes.fulfilled, (state, action) => {
        state.loading.quizzes = false;
        state.quizzes = action.payload.quizzes;
      })
      .addCase(generateQuizzes.rejected, (state, action) => {
        state.loading.quizzes = false;
        state.error = action.payload;
      })
      // Quizzes fetch
      .addCase(fetchQuizzes.fulfilled, (state, action) => {
        state.quizzes = action.payload.quizzes;
      })
      // Explain Concept
      .addCase(explainConcept.pending, (state) => {
        state.loading.explain = true;
        state.error = null;
      })
      .addCase(explainConcept.fulfilled, (state, action) => {
        state.loading.explain = false;
        // add to front of list
        state.explanations.unshift(action.payload.explanation);
      })
      .addCase(explainConcept.rejected, (state, action) => {
        state.loading.explain = false;
        state.error = action.payload;
      })
      // Fetch explanations
      .addCase(fetchExplanations.fulfilled, (state, action) => {
        state.explanations = action.payload.explanations;
      })
      // Fetch Chat
      .addCase(fetchChatHistory.fulfilled, (state, action) => {
        state.chatHistory = action.payload.history;
      })
      // Send Chat message
      .addCase(sendChatMessage.pending, (state) => {
        state.loading.chat = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading.chat = false;
        // The assistant message
        state.chatHistory.push(action.payload.chat);
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading.chat = false;
        state.error = action.payload;
      });
  }
});

export const { clearCurrentDocument, clearQuizzes, clearError, appendUserMessage } = docSlice.actions;
export default docSlice.reducer;
