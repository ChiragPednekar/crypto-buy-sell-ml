import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_URL } from '../App';
import { Bitcoin, TrendingUp, Activity, Send } from 'lucide-react';
import { createChart } from 'lightweight-charts';

export default function Dashboard({ token }) {
  const [prediction, setPrediction] = useState(null);
  const [tradeAmount, setTradeAmount] = useState('');
  const [executing, setExecuting] = useState(false);
  
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const mockCandleTime = useRef(Math.floor(Date.now() / 1000));

  useEffect(() => {
    // Phase 3: Setup TradingView Lightweight-Charts Engine natively (used by Zerodha)
    if (chartContainerRef.current && !chartRef.current) {
        chartRef.current = createChart(chartContainerRef.current, {
            layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#cbd5e1' },
            grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
            timeScale: { timeVisible: true, secondsVisible: false },
        });
        seriesRef.current = chartRef.current.addCandlestickSeries({
            upColor: '#10b981', downColor: '#ef4444', borderVisible: false,
            wickUpColor: '#10b981', wickDownColor: '#ef4444'
        });
        
        // Generate placeholder dummy history matching $43k levels to seed context
        const initialData = [];
        let price = 43000;
        for(let i=100; i>0; i--) {
            price += (Math.random() - 0.5) * 50;
            initialData.push({ time: mockCandleTime.current - (i * 60), open: price, high: price+20, low: price-20, close: price+Math.random()*10 });
        }
        seriesRef.current.setData(initialData);
    }

    // Phase 3: Transition to Zero-Latency FastAPI WebSocket Pipelines
    const ws = new WebSocket(API_URL.replace('http', 'ws') + '/ws/market');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setPrediction(data);
        
        // Feed live ticks directly into TradingView candlestick rendering!
        if (seriesRef.current) {
            mockCandleTime.current += 1;
            const liveTick = {
                time: mockCandleTime.current,
                open: data.price - 5,
                high: data.price + 10,
                low: data.price - 10,
                close: data.price
            };
            seriesRef.current.update(liveTick);
        }
    };

    return () => {
      ws.close();
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  const handleTrade = async (type) => {
    if (!tradeAmount || tradeAmount <= 0) return alert("Enter valid amount");
    setExecuting(true);
    try {
      const btcAmount = parseFloat(tradeAmount) / (prediction?.price || 1);
      await axios.post(`${API_URL}/trade`, 
        { type, price: prediction.price, quantity: btcAmount },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      alert(`Successfully submitted ${type} order!`);
      setTradeAmount('');
    } catch (err) {
      alert(err.response?.data?.detail || "Trade failed");
    } finally {
      setExecuting(false);
    }
  };

  if (!prediction) {
    return <div className="flex h-64 items-center justify-center text-slate-400">Loading High-Frequency AI Pipeline...</div>;
  }

  const isBuy = prediction.signal === 'BUY';
  const isSell = prediction.signal === 'SELL';
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 flex flex-col gap-6">
        
        <div className="glass-card flex justify-between items-center group">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-500/20 rounded-full"><Bitcoin className="w-8 h-8 text-orange-500" /></div>
            <div>
              <p className="text-sm font-medium text-slate-400">Bitcoin (BTC)</p>
              <h2 className="text-3xl font-bold tracking-tight">${prediction.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</h2>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-emerald-400 font-medium bg-emerald-400/10 px-3 py-1 rounded-lg">
              <TrendingUp className="w-4 h-4" /> Live WebSocket
            </div>
          </div>
        </div>

        <div className={`glass-card relative overflow-hidden group border-l-4 ${isBuy ? 'border-l-emerald-500 shadow-emerald-500/10' : isSell ? 'border-l-rose-500 shadow-rose-500/10' : 'border-l-blue-500 shadow-blue-500/10'}`}>
          <div className="absolute top-0 right-0 w-64 h-64 bg-slate-100/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />
          <div className="flex justify-between items-start mb-8 relative z-10">
            <div>
              <p className="text-sm font-medium tracking-wider text-slate-400 mb-1">PERSONALIZED AI SIGNAL</p>
              <h1 className={`text-6xl font-black tracking-tighter ${isBuy ? 'text-emerald-400' : isSell ? 'text-rose-400' : 'text-blue-400'}`}>
                {prediction.signal}
              </h1>
            </div>
            <div className="text-right"><Activity className={`w-8 h-8 ${isBuy ? 'text-emerald-500' : isSell ? 'text-rose-500' : 'text-blue-500'}`} /></div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
            <div className="bg-slate-900/40 rounded-xl p-4">
              <p className="text-sm text-slate-400 mb-1">Confidence Rating</p>
              <p className="text-2xl font-bold">{(prediction.confidence * 100).toFixed(1)}%</p>
            </div>
            
            <div className="bg-slate-900/40 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1.5">Algorithmic Regime</p>
                <div className="flex">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${
                    prediction.regime === 1 ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' :
                    prediction.regime === 2 ? 'text-rose-400 bg-rose-500/10 border border-rose-500/20' :
                    prediction.regime === 3 ? 'text-amber-400 bg-amber-500/10 border border-amber-500/20 animate-pulse' :
                    'text-blue-400 bg-blue-500/10 border border-blue-500/20'
                  }`}>
                    {prediction.regime === 1 ? 'Trending Up' :
                     prediction.regime === 2 ? 'Trending Down' :
                     prediction.regime === 3 ? 'High Volatility' :
                     'Sideways'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/40 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1.5">Market Volatility</p>
                <div className="flex items-center gap-2">
                  <span className={`text-2xl font-bold ${
                    prediction.volatility > 0.02 ? 'text-rose-400' :
                    prediction.volatility > 0.01 ? 'text-amber-400' :
                    'text-emerald-400'
                  }`}>
                    {(prediction.volatility * 100).toFixed(2)}%
                  </span>
                  <span className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    prediction.volatility > 0.02 ? 'bg-rose-500/10 text-rose-400' :
                    prediction.volatility > 0.01 ? 'bg-amber-500/10 text-amber-400' :
                    'bg-emerald-500/10 text-emerald-400'
                  }`}>
                    {prediction.volatility > 0.02 ? 'Risk High' :
                     prediction.volatility > 0.01 ? 'Moderate' :
                     'Low'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/40 rounded-xl p-4">
              <p className="text-sm text-slate-400 mb-1">Projected Price (10h)</p>
              <p className={`text-2xl font-bold ${prediction.predicted_future_price > prediction.price ? 'text-emerald-400' : prediction.predicted_future_price < prediction.price ? 'text-rose-400' : 'text-slate-100'}`}>
                ${prediction.predicted_future_price ? prediction.predicted_future_price.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-semibold text-lg flex items-center gap-2"><Activity className="w-5 h-5 text-blue-500"/> TradingView Engine</h3>
          </div>
          <div className="h-64 w-full" ref={chartContainerRef}></div>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <div className="glass-card">
          <h3 className="font-semibold text-lg mb-6 flex items-center gap-2"><Send className="w-5 h-5 text-emerald-500" /> Executive Order Routing</h3>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-400 mb-2">Amount (USD)</label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-slate-400">$</span>
              <input type="number" placeholder="1000" className="input-base pl-8" value={tradeAmount} onChange={e => setTradeAmount(e.target.value)} />
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-4 mb-6 flex justify-between items-center text-sm">
            <span className="text-slate-400">Yielding Receipt</span>
            <span className="font-bold text-lg">{tradeAmount ? (parseFloat(tradeAmount) / prediction.price).toFixed(6) : "0.000000"} <span className="text-orange-500 text-sm">BTC</span></span>
          </div>

          <div className="flex flex-col gap-3">
             <button disabled={executing} onClick={() => handleTrade('BUY')} className="btn-buy">{executing ? 'Routing...' : 'BUY BTC'}</button>
             <button disabled={executing} onClick={() => handleTrade('SELL')} className="btn-sell">{executing ? 'Routing...' : 'SELL BTC'}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
