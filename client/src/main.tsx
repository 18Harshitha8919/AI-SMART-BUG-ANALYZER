import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.tsx'
import './index.css'

// Configure global API baseURL for Axios requests (useful for production deployment on Render)
const apiURL = import.meta.env.VITE_API_URL;
if (apiURL) {
  axios.defaults.baseURL = apiURL;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
