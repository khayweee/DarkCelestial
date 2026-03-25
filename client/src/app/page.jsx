'use client';

import React, { useState, useEffect } from 'react';
import './page.css';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('Connecting to WebSocket...');

  useEffect(() => {
    // Connect to Backend WebSocket
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus('Connected (Live Data)');
    };

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
      } catch (err) {
        console.error('Error parsing WS message', err);
      }
    };

    ws.onclose = () => {
      setStatus('Disconnected. Reconnecting...');
    };

    return () => ws.close();
  }, []);

  return (
    <main className="dashboard-container">
      <header className="dashboard-header">
        <h1 className="title text-gradient">Trading Assistant</h1>
        <p className="subtitle">
          Real-time entry & exit points computed via advanced technicals (RSI, MACD, EMA) across Crypto and NYSE markets.
        </p>
      </header>

      <div className="dashboard-grid">
        {/* Main Chart Area */}
        <section className="glass-panel chart-section">
          <h2 className="section-title">BTC/USDT Live Chart</h2>
          <div className="chart-container">
             <div className="chart-grid-bg"></div>
             
             <div className="data-overlay" style={{ position: 'relative', zIndex: 10, textAlign: 'center' }}>
               {data && data.latest_price ? (
                 <>
                   <div className="price-display" style={{ fontSize: '3.5rem', fontWeight: 900, textShadow: '0 4px 12px rgba(0,0,0,0.5)', marginBottom: '0.5rem' }}>
                     ${data.latest_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                   </div>
                   <p className="status-text text-secondary" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                     <span className="pulse-indicator" style={{ display: 'inline-block', marginRight: '8px' }}></span>
                     {status}
                   </p>
                 </>
               ) : (
                 <p className="loading-text">
                   <span className="pulse-indicator"></span>
                   {status}
                 </p>
               )}
             </div>
          </div>
        </section>

        {/* Signals and Indicators Sidebar */}
        <aside className="sidebar">
          {/* Signal Panel */}
          <div className="glass-panel signal-panel">
             <h3 className="panel-heading">Latest Signal</h3>
             <div className={`signal-value ${data?.signal === 'BUY' ? 'bullish-glow' : data?.signal === 'SELL' ? 'text-bearish' : 'text-blue'}`}>
               {data?.signal || 'WAITING'}
             </div>
             <p className="signal-reason">{data?.reason || 'Gathering tick data...'}</p>
          </div>
          
          {/* Technicals Panel */}
          <div className="glass-panel technicals-panel">
             <h3 className="panel-heading">Technicals</h3>
             <ul className="indicator-list">
               <li className="indicator-item">
                 <span className="indicator-name">RSI (14)</span>
                 <span className={`indicator-val ${data?.rsi < 30 ? 'text-bullish' : data?.rsi > 70 ? 'text-bearish' : ''}`}>
                   {data?.rsi !== null && data?.rsi !== undefined ? data.rsi : '--'}
                 </span>
               </li>
               <li className="indicator-item">
                 <span className="indicator-name">MACD (12, 26)</span>
                 <span className={`indicator-val ${data?.macd > 0 ? 'text-bullish' : data?.macd < 0 ? 'text-bearish' : ''}`}>
                   {data?.macd !== null && data?.macd !== undefined ? data.macd : '--'}
                 </span>
               </li>
               <li className="indicator-item">
                 <span className="indicator-name">EMA (200)</span>
                 <span className="indicator-val text-blue">
                   {data?.ema !== null && data?.ema !== undefined ? `$${data.ema.toLocaleString()}` : '--'}
                 </span>
               </li>
             </ul>
          </div>
        </aside>
      </div>
    </main>
  );
}
