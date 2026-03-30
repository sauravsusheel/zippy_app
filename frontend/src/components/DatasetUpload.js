import React, { useState, useRef, useCallback } from 'react';
import './DatasetUpload.css';

const ACCEPTED_TYPES = ['.csv', '.xlsx', '.xls', '.json', '.pdf'];
const ACCEPTED_MIME = [
  'text/csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/json',
  'application/pdf',
];

function DatasetUpload({ onUploadSuccess, activeDataset }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);
  const dragCounter = useRef(0);

  const isValidFile = (file) => {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    return ACCEPTED_TYPES.includes(ext) || ACCEPTED_MIME.includes(file.type);
  };

  const uploadFile = useCallback(async (file) => {
    if (!isValidFile(file)) {
      setError('Unsupported file type. Use CSV, XLSX, XLS, JSON or PDF.');
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
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  // ── Drag handlers ──────────────────────────────────────────────
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragging(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current === 0) setDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    dragCounter.current = 0;

    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) uploadFile(file);
  };

  const handleReset = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/reset-dataset', { method: 'POST' });
      if (response.ok) {
        onUploadSuccess({ table_name: 'sales', file_name: null, rows: 'Sample', columns: 'Multiple' });
      }
    } catch {
      setError('Failed to reset dataset');
    }
  };

  const fileIcon = (filename) => {
    if (!filename) return '📊';
    const ext = filename.split('.').pop().toLowerCase();
    return { csv: '📄', xlsx: '📊', xls: '📊', json: '🗂️', pdf: '📕' }[ext] || '📁';
  };

  return (
    <div className="dataset-upload-container">
      <div className="upload-section">
        <h3>📁 Upload Dataset</h3>

        {/* Drag & Drop Zone */}
        <div
          className={`drop-zone ${dragging ? 'drop-zone--active' : ''} ${uploading ? 'drop-zone--uploading' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_TYPES.join(',')}
            onChange={handleFileSelect}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          {uploading ? (
            <div className="drop-zone__uploading">
              <div className="spinner" />
              <p>Uploading...</p>
            </div>
          ) : dragging ? (
            <div className="drop-zone__content">
              <span className="drop-zone__icon">📂</span>
              <p>Drop it!</p>
            </div>
          ) : (
            <div className="drop-zone__content">
              <span className="drop-zone__icon">⬆️</span>
              <p><strong>Drag & drop</strong> your file here</p>
              <p className="drop-zone__sub">or click to browse</p>
              <div className="drop-zone__types">
                <span>CSV</span><span>XLSX</span><span>XLS</span><span>JSON</span><span>PDF</span>
              </div>
            </div>
          )}
        </div>

        <div className="upload-actions">
          <button className="reset-button" onClick={handleReset} disabled={uploading}>
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
              {fileIcon(activeDataset.file_name)} {activeDataset.uploaded ? 'Custom Dataset' : 'Sample Dataset'}
            </div>
            <div className="dataset-details">
              <p><strong>Table:</strong> {activeDataset.table_name}</p>
              {activeDataset.file_name && <p><strong>File:</strong> {activeDataset.file_name}</p>}
              <p><strong>Rows:</strong> {activeDataset.rows}</p>
              <p><strong>Columns:</strong> {activeDataset.columns}</p>
            </div>
          </div>
        )}
      </div>

      {activeDataset?.schema && (
        <div className="schema-section">
          <h4>📋 Dataset Schema</h4>
          <div className="schema-table">
            <table>
              <thead>
                <tr><th>Column Name</th><th>Data Type</th></tr>
              </thead>
              <tbody>
                {activeDataset.schema.columns?.map((col, idx) => (
                  <tr key={idx}>
                    <td>{col.name}</td>
                    <td><span className="type-badge">{col.type}</span></td>
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
