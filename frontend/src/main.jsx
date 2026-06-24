// frontend/src/main.jsx
/**
 * Purpose: Entrypoint for Vite React client.
 * Responsibilities:
 * - Render React DOM.
 * - Wrap App in Redux Provider.
 * - Import global Tailwind stylesheet.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import store from './redux/store';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
