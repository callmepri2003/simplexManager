import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter } from "react-router-dom";
import ResponsiveDrawer from './components/ResponsiveDrawer.jsx';


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ResponsiveDrawer/>
    </BrowserRouter>
  </StrictMode>
)
