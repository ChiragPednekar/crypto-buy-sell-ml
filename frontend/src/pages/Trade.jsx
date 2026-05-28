import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../App';
import { Activity, ShieldAlert, Target } from 'lucide-react';

export default function Trade({ token }) {
  const [prediction, setPrediction] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [tradeAmount, setTradeAmount] = useState('');
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [predRes, portRes] = await Promise.all([
        axios.get(`${API_URL}/predict`),
        axios.get(`${API_URL}/portfolio`, { headers: { Authorization: `Bearer ${token}` }})
      ]);
      setPrediction(predRes.data);
      setData(portRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const currentPrice = prediction?.current_price || 0;
  const isBuy = prediction?.signal === 'BUY';
  const isSell = prediction?.signal === 'SELL';

  const handleTrade = async (type) => {
    if (!tradeAmount || Number(tradeAmount) <= 0) return alert("Enter valid USD amount.");
    setExecuting(true);
    try {
      const qty = parseFloat(tradeAmount) / currentPrice;
      await axios.post(`${API_URL}/trade`, 
        { type, price: currentPrice, quantity: qty },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`${type} order submitted!`);
      setTradeAmount('');
      fetchData(); // refresh balances
    } catch (err) {
      alert(err.response?.data?.detail || "Execution failed.");
    } finally {
      setExecuting(false);
    }
  };

  if (loading || !prediction) {
    return <div className="flex h-64 items-center justify-center text-slate-400">Loading Execution Environment...</div>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
      
      {/* TRADE EXECUTION PANEL */}
      <div className="glass-card">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
           <Target className="text-blue-500 w-5 h-5"/>
           Focused Execution
        </h2>
        
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-2">Order Size (USD)</label>
          <div className="relative">
            <span className="absolute left-4 top-3 text-slate-400 font-semibold">$</span>
            <input 
              type="number" 
              className="input-base pl-8 text-xl" 
              placeholder="0.00"
              value={tradeAmount}
              onChange={e => setTradeAmount(e.target.value)}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs">
             <span className="text-slate-500">Available: ${data?.balance.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
             <span className="text-slate-500">Max BTC: {data?.btc_amount.toFixed(4)} ₿</span>
          </div>
        </div>

        <div className="glass-card bg-slate-900/40 p-4 border-none mb-8 flex justify-between items-center text-sm">
          <span className="text-slate-400">Estimated Delivery</span>
          <span className="font-bold text-xl">
             {tradeAmount ? (parseFloat(tradeAmount) / currentPrice).toFixed(6) : "0.000000"} 
             <span className="text-orange-500 text-sm ml-1">BTC</span>
          </span>
        </div>

        <div className="grid grid-cols-2 gap-4">
           <button 
             onClick={() => handleTrade('BUY')}
             disabled={executing}
             className="btn-buy py-4 text-lg">
             BUY NOW
           </button>
           <button 
             onClick={() => handleTrade('SELL')}
             disabled={executing}
             className="btn-sell py-4 text-lg">
             SELL NOW
           </button>
        </div>
      </div>

      {/* AI MODEL INSIGHT PANEL */}
      <div className="glass-card flex flex-col justify-between">
        <div>
           <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Activity className="text-purple-500 w-5 h-5"/>
              Algorithmic Insight
           </h2>
           
           <div className="space-y-6">
              <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl">
                 <span className="text-slate-400 font-medium">Model Output</span>
                 <span className={`font-bold px-3 py-1 rounded-lg ${isBuy ? 'bg-emerald-500/20 text-emerald-400' : isSell ? 'bg-rose-500/20 text-rose-400' : 'bg-blue-500/20 text-blue-400'}`}>
                    {prediction.signal}
                 </span>
              </div>
              
              <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl">
                 <span className="text-slate-400 font-medium">Algorithm Confidence</span>
                 <span className="font-bold">{(prediction.confidence*100).toFixed(2)}%</span>
              </div>
              
              <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl">
                 <span className="text-slate-400 font-medium">Macro Regime Identifier</span>
                 <span className="font-bold capitalize">{prediction.regime === 1 ? 'Trending Up' : prediction.regime === 2 ? 'Trending Down' : prediction.regime === 3 ? 'High Volatility' : 'Sideways'}</span>
              </div>

              <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl">
                 <span className="text-slate-400 font-medium">Volatility Score</span>
                 <span className={`font-bold ${
                    prediction.volatility > 0.02 ? 'text-rose-400' :
                    prediction.volatility > 0.01 ? 'text-amber-400' :
                    'text-emerald-400'
                 }`}>
                    {(prediction.volatility * 100).toFixed(2)}%
                 </span>
              </div>

              <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl">
                 <span className="text-slate-400 font-medium">Projected Target (10h)</span>
                 <span className={`font-bold ${prediction.predicted_future_price > currentPrice ? 'text-emerald-400' : prediction.predicted_future_price < currentPrice ? 'text-rose-400' : 'text-slate-300'}`}>
                    ${prediction.predicted_future_price ? prediction.predicted_future_price.toLocaleString(undefined, {minimumFractionDigits: 2}) : '0.00'}
                 </span>
              </div>

              <div className="flex justify-between items-center border border-slate-700/50 border-dashed p-4 rounded-xl">
                 <span className="text-slate-500 font-medium flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4"/> Execution Price Guard
                 </span>
                 <span className="font-bold text-slate-300">${currentPrice.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
              </div>
           </div>
        </div>
        
        <p className="text-xs text-slate-500 text-center mt-8">
           Data is actively sourced from Binance USD spot markets in 5-second polling intervals.
        </p>
      </div>

    </div>
  );
}
