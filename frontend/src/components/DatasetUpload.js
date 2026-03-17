import React, { useState, useRef } from 'react';
import './DatasetUpload.css';

function DatasetUpload({ onUploadSuccess, activeDataset }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      setError('Only CSV and XLSX files are supported');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload-dataset', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      onUploadSuccess(data);
      setError(null);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleReset = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/reset-dataset', {
        method: 'POST',
      });

      if (response.ok) {
        onUploadSuccess({
          table_name: 'sales',
          file_name: null,
          rows: 'Sample',
          columns: 'Multiple',
        });
      }
    } catch (err) {
      setError('Failed to reset dataset');
    }
  };

  return (
    <div className="dataset-upload-container">
      <div className="upload-section">
        <h3>📁 Upload Dataset</h3>
        
        <div className="upload-controls">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx"
            onChange={handleFileSelect}
            disabled={uploading}
            className="file-input"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="upload-button">
            {uploading ? '⏳ Uploading...' : '📤 Choose File'}
          </label>
          
          <button 
            className="reset-button"
            onClick={handleReset}
            disabled={uploading}
          >
            🔄 Reset to Sample Data
          </button>
        </div>

        {error && (
          <div className="upload-error">
            <span>⚠️</span>
            <p>{error}</p>
          </div>
        )}

        {activeDataset && (
          <div className="active-dataset-info">
            <div className="dataset-badge">
              {activeDataset.uploaded ? '📊 Custom Dataset' : '📊 Sample Dataset'}
            </div>
            <div className="dataset-details">
              <p><strong>Table:</strong> {activeDataset.table_name}</p>
              {activeDataset.file_name && (
                <p><strong>File:</strong> {activeDataset.file_name}</p>
              )}
              <p><strong>Rows:</strong> {activeDataset.rows}</p>
              <p><strong>Columns:</strong> {activeDataset.columns}</p>
            </div>
          </div>
        )}
      </div>

      {activeDataset && activeDataset.schema && (
        <div className="schema-section">
          <h4>📋 Dataset Schema</h4>
          <div className="schema-table">
            <table>
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Data Type</th>
                </tr>
              </thead>
              <tbody>
                {activeDataset.schema.columns && activeDataset.schema.columns.map((col, idx) => (
                  <tr key={idx}>
                    <td>{col.name}</td>
                    <td className="type-badge">{col.type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default DatasetUpload;
