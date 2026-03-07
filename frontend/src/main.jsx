import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Add Professional Google Fonts
const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap';
link.rel = 'stylesheet';
document.head.appendChild(link);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
