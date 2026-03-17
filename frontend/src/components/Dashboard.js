import React from 'react';
import './Dashboard.css';
import ChartRenderer from './ChartRenderer';

function Dashboard({ data }) {
  const { sql, data: queryData, chart_config } = data;

  // Generate natural language summary from data
  const generateNLPSummary = () => {
    if (!queryData || queryData.length === 0) {
      return "No data found for your query.";
    }

    let summary = "";
    
    // Count records
    summary += `Found ${queryData.length} record${queryData.length !== 1 ? 's' : ''}.\n\n`;

    // Get column names
    const columns = Object.keys(queryData[0]);
    
    // Analyze numeric columns
    const numericColumns = columns.filter(col => {
      const firstVal = queryData[0][col];
      return typeof firstVal === 'number' || !isNaN(parseFloat(firstVal));
    });

    // Generate summaries for numeric columns
    if (numericColumns.length > 0) {
      summary += "📊 Summary Statistics:\n";
      
      numericColumns.forEach(col => {
        const values = queryData.map(row => parseFloat(row[col])).filter(v => !isNaN(v));
        
        if (values.length > 0) {
          const sum = values.reduce((a, b) => a + b, 0);
          const avg = sum / values.length;
          const max = Math.max(...values);
          const min = Math.min(...values);
          
          summary += `\n• ${col}:\n`;
          summary += `  - Total: ${sum.toFixed(2)}\n`;
          summary += `  - Average: ${avg.toFixed(2)}\n`;
          summary += `  - Maximum: ${max.toFixed(2)}\n`;
          summary += `  - Minimum: ${min.toFixed(2)}\n`;
        }
      });
    }

    // Show top records
    if (queryData.length > 0) {
      summary += "\n📋 Top Records:\n";
      queryData.slice(0, 5).forEach((row, idx) => {
        summary += `\n${idx + 1}. `;
        summary += Object.entries(row)
          .map(([key, val]) => `${key}: ${val}`)
          .join(", ");
      });
      
      if (queryData.length > 5) {
        summary += `\n\n... and ${queryData.length - 5} more records`;
      }
    }

    return summary;
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 Query Results</h2>
        <div className="result-count">
          {queryData.length} record{queryData.length !== 1 ? 's' : ''} found
        </div>
      </div>

      {/* Chart Section - First */}
      <div className="chart-card">
        <div className="chart-section">
          <ChartRenderer config={chart_config} data={queryData} />
        </div>
      </div>

      {/* Natural Language Summary - Below Chart */}
      <div className="nlp-summary-section">
        <h3>📝 Natural Language Summary</h3>
        <div className="nlp-content">
          {generateNLPSummary().split('\n').map((line, idx) => (
            <p key={idx} style={{ marginBottom: line.trim() === '' ? '10px' : '0' }}>
              {line}
            </p>
          ))}
        </div>
      </div>

      {/* SQL Query */}
      <div className="sql-section">
        <details>
          <summary>🔍 View Generated SQL Query</summary>
          <pre className="sql-code">{sql}</pre>
        </details>
      </div>

      {/* Raw Data Table */}
      {queryData.length > 0 && (
        <div className="data-preview">
          <details>
            <summary>📋 View Raw Data ({queryData.length} rows)</summary>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    {Object.keys(queryData[0]).map((key) => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {queryData.slice(0, 100).map((row, idx) => (
                    <tr key={idx}>
                      {Object.values(row).map((value, vidx) => (
                        <td key={vidx}>{value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {queryData.length > 100 && (
                <p className="table-note">Showing first 100 rows of {queryData.length}</p>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
