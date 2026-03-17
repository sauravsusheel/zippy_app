import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './ChartRenderer.css';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];

function ChartRenderer({ config, data }) {
  if (!config || !data || data.length === 0) {
    return <div className="no-data">No data to display</div>;
  }

  const { type, xAxis, yAxis, nameKey, dataKey } = config;

  // If chart type is "none", don't render anything
  if (type === "none") {
    return null;
  }

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxis} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey={yAxis} fill="#667eea" />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxis} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey={yAxis} stroke="#667eea" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );

  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <PieChart>
        <Pie
          data={data}
          dataKey={dataKey}
          nameKey={nameKey}
          cx="50%"
          cy="50%"
          outerRadius={120}
          label
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );

  const renderMultiBarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxis} />
        <YAxis />
        <Tooltip />
        <Legend />
        {yAxis.map((key, idx) => (
          <Bar key={key} dataKey={key} fill={COLORS[idx % COLORS.length]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );

  const renderTable = () => (
    <div className="table-container">
      <table className="chart-table">
        <thead>
          <tr>
            {Object.keys(data[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {Object.values(row).map((value, vidx) => (
                <td key={vidx}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="chart-renderer">
      <div className="chart-title">
        {type === 'bar' && '📊 Bar Chart'}
        {type === 'line' && '📈 Line Chart'}
        {type === 'pie' && '🥧 Pie Chart'}
        {type === 'multibar' && '📊 Multi-Series Bar Chart'}
        {type === 'table' && '📋 Data Table'}
      </div>
      
      {type === 'bar' && renderBarChart()}
      {type === 'line' && renderLineChart()}
      {type === 'pie' && renderPieChart()}
      {type === 'multibar' && renderMultiBarChart()}
      {type === 'table' && renderTable()}
    </div>
  );
}

export default ChartRenderer;
