import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Portfolio from './pages/Portfolio';
import Trade from './pages/Trade';
import Login from './pages/Login';

export const API_URL = "http://localhost:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);

  const login = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <Login onLogin={login} />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
        <Navbar onLogout={logout} />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8">
          <Routes>
            <Route path="/" element={<Dashboard token={token} />} />
            <Route path="/portfolio" element={<Portfolio token={token} />} />
            <Route path="/trade" element={<Trade token={token} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
