import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import App from './App'
import { BootstrapProvider } from './lib/bootstrap'
import './app.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <BootstrapProvider>
        <App />
      </BootstrapProvider>
    </BrowserRouter>
  </StrictMode>,
)
