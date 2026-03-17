import React from 'react';
import './Dashboard.css';
import ChartRenderer from './ChartRenderer';

function Dashboard({ data }) {
  const { sql, data: queryData, chart_config, insights } = data;

  // Generate concise data summary
  const generateDataSummary = () => {
    if (!queryData || queryData.length === 0) {
      return "No data found for your query.";
    }

    let summary = `Found ${queryData.length} record${queryData.length !== 1 ? 's' : ''}.`;
    
    // Get column names
    const columns = Object.keys(queryData[0]);
    
    // Analyze numeric columns for quick stats
    const numericColumns = columns.filter(col => {
      const firstVal = queryData[0][col];
      return typeof firstVal === 'number' || !isNaN(parseFloat(firstVal));
    });

    // Add quick numeric summary
    if (numericColumns.length > 0) {
      summary += " Key metrics: ";
      const stats = numericColumns.slice(0, 2).map(col => {
        const values = queryData.map(row => parseFloat(row[col])).filter(v => !isNaN(v));
        if (values.length > 0) {
          const sum = values.reduce((a, b) => a + b, 0);
          const avg = sum / values.length;
          return `${col} (avg: ${avg.toFixed(2)})`;
        }
        return null;
      }).filter(Boolean).join(", ");
      summary += stats;
    }

    return summary;
  };

  const shouldShowChart = chart_config && chart_config.type && chart_config.type !== "none";

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>📊 Query Results</h2>
        <div className="result-count">
          {queryData.length} record{queryData.length !== 1 ? 's' : ''} found
        </div>
      </div>

      {/* Chart Section - Only if needed */}
      {shouldShowChart && (
        <div className="chart-card">
          <div className="chart-section">
            <ChartRenderer config={chart_config} data={queryData} />
          </div>
        </div>
      )}

      {/* AI-Generated Insights - Primary Response */}
      {insights && (
        <div className="insights-section">
          <h3>💡 Analysis</h3>
          <div className="insights-content">
            <p>{insights}</p>
          </div>
        </div>
      )}

      {/* Data Summary */}
      <div className="data-summary-section">
        <h3>📈 Data Summary</h3>
        <div className="summary-content">
          <p>{generateDataSummary()}</p>
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
