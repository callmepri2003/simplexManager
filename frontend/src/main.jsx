import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter } from "react-router-dom";
import ResponsiveDrawer from './components/ResponsiveDrawer.jsx';
import { AuthProvider } from './components/AuthContext.jsx';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <BrowserRouter>
          <ResponsiveDrawer/>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>
)
