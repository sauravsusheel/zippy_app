import React, { useState, useEffect } from 'react';
import './DatasetPreview.css';

function DatasetPreview({ activeDataset }) {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (activeDataset && activeDataset.table_name) {
      fetchPreview();
    }
  }, [activeDataset]);

  const fetchPreview = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/dataset-preview?table_name=${activeDataset.table_name}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch preview');
      }

      const data = await response.json();
      setPreview(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!activeDataset) {
    return null;
  }

  return (
    <div className="dataset-preview-container">
      <div className="preview-header">
        <h3>👁️ Dataset Preview</h3>
        <button 
          className="refresh-button"
          onClick={fetchPreview}
          disabled={loading}
        >
          {loading ? '⏳' : '🔄'} Refresh
        </button>
      </div>

      {error && (
        <div className="preview-error">
          <span>⚠️</span>
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="preview-loading">
          <div className="spinner"></div>
          <p>Loading preview...</p>
        </div>
      )}

      {preview && preview.success && (
        <div className="preview-content">
          <div className="preview-stats">
            <div className="stat">
              <span className="stat-label">Total Rows</span>
              <span className="stat-value">{preview.total_rows}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Columns</span>
              <span className="stat-value">{preview.columns.length}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Preview Rows</span>
              <span className="stat-value">{preview.preview_rows}</span>
            </div>
          </div>

          <div className="preview-table-wrapper">
            <table className="preview-table">
              <thead>
                <tr>
                  {preview.columns.map((col, idx) => (
                    <th key={idx}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.data.map((row, idx) => (
                  <tr key={idx}>
                    {preview.columns.map((col, cidx) => (
                      <td key={cidx}>{String(row[col]).substring(0, 50)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {preview.total_rows > preview.preview_rows && (
            <p className="preview-note">
              Showing {preview.preview_rows} of {preview.total_rows} rows
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default DatasetPreview;
