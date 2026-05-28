import React, { useState } from 'react';
import { API_URL } from '../App';
import { Activity } from 'lucide-react';

export default function Login({ onLogin }) {
  const [isSign, setIsSign] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (!isSign) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const res = await fetch(`${API_URL}/token`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData
        });
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        onLogin(data.access_token);
      } else {
        const res = await fetch(`${API_URL}/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        if (!res.ok) throw new Error(await res.text());
        setIsSign(false);
        alert("Account Created! Please Login.");
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-900">
      <div className="glass-card w-full max-w-md">
        <div className="flex justify-center mb-8">
          <div className="flex items-center gap-2 text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            <Activity className="text-blue-500" />
            AI BTC Trader
          </div>
        </div>
        
        <h2 className="text-xl text-center font-semibold mb-6">
          {isSign ? 'Create Account' : 'Trader Login'}
        </h2>
        
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input 
            type="email" 
            className="input-base" 
            placeholder="Email Address" 
            value={email} 
            onChange={e => setEmail(e.target.value)} 
            required 
          />
          <input 
            type="password" 
            className="input-base" 
            placeholder="Secure Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
          />
          <button disabled={loading} type="submit" className="btn-primary mt-2 flex justify-center items-center gap-2">
            {loading ? <Activity className="w-5 h-5 animate-spin"/> : (isSign ? 'Sign Up' : 'Login ->')}
          </button>
        </form>
        
        <p className="text-center mt-6 text-slate-400 text-sm cursor-pointer hover:text-slate-300 transition-colors" 
           onClick={() => setIsSign(!isSign)}>
          {isSign ? 'Already have an account? Login' : "Don't have an account? Create one"}
        </p>
      </div>
    </div>
  );
}
