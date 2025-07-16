import React, { useState } from 'react';
import './App.css';

function App() {
    const [ticker, setTicker] = useState('');
    const [marketPulseData, setMarketPulseData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_BASE_URL = 'http://localhost:8000'; // Make sure FastAPI is running

    const fetchMarketPulse = async () => {
        if (!ticker) {
            setError('Please enter a ticker symbol.');
            setMarketPulseData(null);
            return;
        }

        setLoading(true);
        setError(null);
        setMarketPulseData(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/market-pulse?ticker=${encodeURIComponent(ticker)}`);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            setMarketPulseData(data);
        } catch (err) {
            setError(`Failed to fetch data: ${err.message}`);
            console.error("Fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            fetchMarketPulse();
        }
    };

    const getMomentumScoreClass = (score) => {
        if (score > 0) return 'score-positive';
        if (score < 0) return 'score-negative';
        return '';
    };

    return (
        <div className="container">
            <h1>Stock Market Pulse Analyzer</h1>
            <p className="subtitle">Get real-time stock analysis with momentum, news, and AI-powered recommendations.</p>

            <div className="input-section">
                <input
                    type="text"
                    placeholder="Enter stock ticker (e.g., NVDA, AAPL)"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                    onKeyDown={handleKeyDown}
                    aria-label="Stock Ticker Symbol"
                />
                <button onClick={fetchMarketPulse} disabled={loading}>
                    {loading ? 'Fetching...' : 'Get Pulse'}
                </button>
            </div>

            {loading && <div className="loading-message">Loading data...</div>}
            {error && <div className="error-message">{error}</div>}

            {marketPulseData && (
                <div className="results-section">
                    <h2 className="ticker-header">
                        {marketPulseData.ticker}
                        <span className="as-of-date"> as of {marketPulseData.as_of}</span>
                    </h2>

                    <div className="pulse-summary">
                        <span className={`pulse-badge pulse-${marketPulseData.pulse}`}>
                            {marketPulseData.pulse.toUpperCase()}
                        </span>
                        <p className="llm-explanation">{marketPulseData.llm_explanation}</p>
                    </div>

                    <div className="results-grid">
                        <div className="card momentum-card">
                            <h3>Momentum</h3>
                            <p><strong>Score:</strong>
                                <span className={`momentum-score ${getMomentumScoreClass(marketPulseData.momentum.score)}`}>
                                    {marketPulseData.momentum.score}%
                                </span>
                            </p>
                            <h4>5-Day Returns:</h4>
                            <ul>
                                {marketPulseData.momentum.returns && marketPulseData.momentum.returns.length > 0 ? (
                                    marketPulseData.momentum.returns.map((ret, index) => (
                                        <li key={index} className={`return-item return-${ret >= 0 ? 'positive' : 'negative'}`}>
                                            Day {index + 1}: {ret}%
                                        </li>
                                    ))
                                ) : (
                                    <li>No sufficient return data available.</li>
                                )}
                            </ul>
                        </div>

                        <div className="card news-card">
                            <h3>Latest News</h3>
                            {marketPulseData.news && marketPulseData.news.length > 0 ? (
                                <ul className="news-list">
                                    {marketPulseData.news.map((item, index) => (
                                        <li key={index}>
                                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                                                <strong>{item.title}</strong>
                                            </a>
                                            <p className="news-description">{item.description}</p>
                                            <span className="news-published">{item.published}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No recent news found for this ticker.</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
