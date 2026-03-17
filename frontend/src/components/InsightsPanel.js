import React, { useState } from 'react';
import './InsightsPanel.css';

function InsightsPanel({ query, data, onGenerateInsights }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateInsights = async () => {
    setLoading(true);
    setError(null);
    setInsights(null);

    try {
      const response = await fetch('http://localhost:8000/api/generate-insights', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
        }),
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.detail || result.error || 'Failed to generate insights');
      }
      
      if (result.success) {
        setInsights(result.insights);
        if (onGenerateInsights) {
          onGenerateInsights(result.insights);
        }
      } else {
        setError(result.error || 'Failed to generate insights');
      }
    } catch (err) {
      console.error('Insights error:', err);
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="insights-panel-container">
      <button
        className="generate-insights-btn"
        onClick={handleGenerateInsights}
        disabled={loading || !query}
      >
        {loading ? (
          <>
            <span className="spinner-small"></span>
            Generating Insights...
          </>
        ) : (
          <>
            💡 Generate AI Insights
          </>
        )}
      </button>

      {error && (
        <div className="insights-error">
          <span>⚠️</span>
          <p>{error}</p>
        </div>
      )}

      {insights && (
        <div className="insights-card">
          <div className="insights-header">
            <h3>🔍 AI Data Analyst Insights</h3>
          </div>
          <div className="insights-content">
            {insights.split('\n').map((line, idx) => {
              const trimmedLine = line.trim();
              if (!trimmedLine) return null;
              
              // Check if line is a bullet point or heading
              if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-') || trimmedLine.startsWith('*')) {
                return (
                  <div key={idx} className="insight-item">
                    <span className="bullet">•</span>
                    <span>{trimmedLine.substring(1).trim()}</span>
                  </div>
                );
              } else if (trimmedLine.endsWith(':')) {
                return (
                  <div key={idx} className="insight-section-title">
                    {trimmedLine}
                  </div>
                );
              } else {
                return (
                  <div key={idx} className="insight-text">
                    {trimmedLine}
                  </div>
                );
              }
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default InsightsPanel;
