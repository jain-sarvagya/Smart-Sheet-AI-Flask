// frontend/src/redux/store.js
/**
 * Purpose: Global Redux Store configuration.
 * Responsibilities:
 * - Combine slices (auth, docs) into a centralized store.
 * - Export configureStore instance for binding to Provider.
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import docReducer from './slices/docSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    docs: docReducer,
  },
});

export default store;
