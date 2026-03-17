import React, { useState } from 'react';
import './QueryInput.css';

function QueryInput({ onSubmit, loading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query);
    }
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-wrapper">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your business data..."
            className="query-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="submit-button"
            disabled={loading || !query.trim()}
          >
            {loading ? '⏳' : '🚀'} {loading ? 'Processing...' : 'Generate Dashboard'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default QueryInput;
