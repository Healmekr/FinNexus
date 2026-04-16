import React from 'react';
import Navbar from './Navbar';
import './Insights.css';

function Insights() {
  return (
    <div className="insights-container">
      <Navbar />
      <div className="insights-content">
        <h1>Financial Insights</h1>
        <p>AI-powered analysis of your spending habits and personalized recommendations.</p>
        <div className="insight-list">
          <div className="insight-item">📈 Your spending increased by 12% this month – consider reviewing subscriptions.</div>
          <div className="insight-item">🎯 Goal: Save $500 by June – you're 60% there.</div>
          <div className="insight-item">🔒 Unusual transaction detected? No, all clear.</div>
        </div>
      </div>
    </div>
  );
}

export default Insights;