import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import Dashboard from './components/Dashboard';
import { CssVarsProvider } from '@mui/joy/styles';
import theme from './theme/theme';

function App() {
  return (
    <CssVarsProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Router>
    </CssVarsProvider>
  );
}

export default App;
