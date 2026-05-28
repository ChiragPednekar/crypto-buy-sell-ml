import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../App';
import { Wallet, DollarSign, Bitcoin, ArrowUpRight, ArrowDownRight, History } from 'lucide-react';

export default function Portfolio({ token }) {
  const [data, setData] = useState(null);
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [portRes, predRes] = await Promise.all([
          axios.get(`${API_URL}/portfolio`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API_URL}/predict`)
        ]);
        setData(portRes.data);
        setPrediction(predRes.data);
      } catch (err) {
        console.error("Error fetching portfolio", err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [token]);

  if (!data || !prediction) {
    return <div className="flex h-64 items-center justify-center text-slate-400">Syncing Ledger...</div>;
  }

  const currentPrice = prediction.current_price || 0;
  
  // Calculate Avg Buy Price and PnL metrics
  let totalInvested = 0;
  let totalBtcBought = 0;
  
  data.trades?.forEach(t => {
    if (t.type === 'BUY') {
      totalInvested += (t.price * t.quantity);
      totalBtcBought += t.quantity;
    }
  });

  const avgBuyPrice = totalBtcBought > 0 ? (totalInvested / totalBtcBought) : 0;
  
  // Current holding value
  const holdingValue = data.btc_amount * currentPrice;
  const originalCostOfHoldings = data.btc_amount * avgBuyPrice;
  
  const pnlUSD = data.btc_amount > 0 ? (holdingValue - originalCostOfHoldings) : 0;
  const pnlPct = data.btc_amount > 0 && originalCostOfHoldings > 0 ? (pnlUSD / originalCostOfHoldings) * 100 : 0;
  
  const isProfit = pnlUSD >= 0;

  return (
    <div className="flex flex-col gap-6">
      
      {/* TOP SUMMARY */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card flex items-center gap-4">
           <div className="p-3 bg-blue-500/20 rounded-xl">
             <DollarSign className="w-8 h-8 text-blue-500" />
           </div>
           <div>
             <p className="text-sm font-medium text-slate-400">Available Balance</p>
             <h2 className="text-2xl font-bold">${data.balance.toLocaleString(undefined, {minimumFractionDigits: 2})}</h2>
           </div>
        </div>

        <div className="glass-card flex items-center gap-4">
           <div className="p-3 bg-orange-500/20 rounded-xl">
             <Bitcoin className="w-8 h-8 text-orange-500" />
           </div>
           <div>
             <p className="text-sm font-medium text-slate-400">BTC Holdings</p>
             <h2 className="text-2xl font-bold">{data.btc_amount.toFixed(4)} ₿</h2>
           </div>
        </div>

        <div className="glass-card flex items-center gap-4">
           <div className="p-3 bg-slate-700/50 rounded-xl">
             <Wallet className="w-8 h-8 text-slate-400" />
           </div>
           <div>
             <p className="text-sm font-medium text-slate-400">Avg Buy Price</p>
             <h2 className="text-2xl font-bold">${avgBuyPrice > 0 ? avgBuyPrice.toLocaleString(undefined, {minimumFractionDigits: 2}) : '0.00'}</h2>
           </div>
        </div>

        <div className={`glass-card flex items-center gap-4 relative overflow-hidden group border-l-4 ${isProfit ? 'border-l-emerald-500 shadow-emerald-500/10' : 'border-l-rose-500 shadow-rose-500/10'}`}>
           <div className="p-3 rounded-xl bg-slate-800">
             {isProfit ? <ArrowUpRight className="w-8 h-8 text-emerald-500" /> : <ArrowDownRight className="w-8 h-8 text-rose-500" />}
           </div>
           <div>
             <p className="text-sm font-medium text-slate-400">Unrealized PnL</p>
             <h2 className={`text-2xl font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
               {isProfit ? '+' : ''}${pnlUSD.toLocaleString(undefined, {minimumFractionDigits: 2})}
             </h2>
             <span className={`text-sm ${isProfit ? 'text-emerald-500' : 'text-rose-500'}`}>
               {isProfit ? '+' : ''}{pnlPct.toFixed(2)}%
             </span>
           </div>
        </div>
      </div>

      {/* TRADE HISTORY TABLE */}
      <div className="glass-card overflow-hidden p-0 relative group">
        <div className="px-6 py-5 border-b border-slate-700/50 flex items-center gap-3">
           <History className="w-5 h-5 text-blue-400" />
           <h3 className="font-semibold text-lg">Transaction History</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-900/50 text-slate-400 uppercase tracking-wider text-xs">
              <tr>
                <th className="px-6 py-4 font-medium">Type</th>
                <th className="px-6 py-4 font-medium">Quantity</th>
                <th className="px-6 py-4 font-medium">Execution Price</th>
                <th className="px-6 py-4 font-medium">Total Value</th>
                <th className="px-6 py-4 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {data.trades?.map((t, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded font-bold text-xs ${t.type === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                      {t.type}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-medium">{t.quantity.toFixed(4)} BTC</td>
                  <td className="px-6 py-4">${t.price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="px-6 py-4">${(t.price * t.quantity).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                  <td className="px-6 py-4 text-slate-500">{new Date(t.timestamp).toLocaleString()}</td>
                </tr>
              ))}
              {(!data.trades || data.trades.length === 0) && (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                    No trading history available. Make your first execution!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
