import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.tsx'
import './index.css'

// Configure global API baseURL for Axios requests (useful for production deployment on Render)
const apiURL = import.meta.env.VITE_API_URL || 'https://bugsense-server.onrender.com';
let cleanURL = apiURL.trim();
if (cleanURL.endsWith('/')) {
  cleanURL = cleanURL.slice(0, -1);
}
if (cleanURL.endsWith('/api')) {
  cleanURL = cleanURL.slice(0, -4);
}
if (!cleanURL.startsWith('http://') && !cleanURL.startsWith('https://')) {
  cleanURL = `https://${cleanURL}`;
}
axios.defaults.baseURL = cleanURL;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
