import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const ResultsChart = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="result-card">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Analysis Trends</h3>
        <p className="text-gray-600">No analysis data available</p>
      </div>
    );
  }

  // Prepare data for charts
  const realCount = data.filter(item => item.label === 'REAL').length;
  const fakeCount = data.filter(item => item.label === 'FAKE').length;
  
  const pieData = [
    { name: 'Real', value: realCount, color: '#10b981' },
    { name: 'Fake', value: fakeCount, color: '#ef4444' }
  ];

  // Prepare time series data (last 10 analyses)
  const timeSeriesData = data.slice(0, 10).reverse().map(item => ({
    name: new Date(item.timestamp).toLocaleDateString(),
    confidence: (item.confidence * 100).toFixed(1),
    type: item.label
  }));

  // Confidence distribution
  const confidenceRanges = {
    'High (80-100%)': data.filter(item => item.confidence >= 0.8).length,
    'Medium (60-79%)': data.filter(item => item.confidence >= 0.6 && item.confidence < 0.8).length,
    'Low (0-59%)': data.filter(item => item.confidence < 0.6).length
  };

  const confidenceData = Object.entries(confidenceRanges).map(([range, count]) => ({
    range,
    count
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Pie Chart - Real vs Fake */}
      <div className="result-card">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Detection Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart - Confidence Distribution */}
      <div className="result-card">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Confidence Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={confidenceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Line Chart - Recent Analyses */}
      <div className="result-card lg:col-span-2">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Recent Analysis Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-2 border border-gray-300 rounded shadow">
                      <p className="font-semibold">{data.name}</p>
                      <p className="text-sm">Confidence: {data.confidence}%</p>
                      <p className="text-sm">Result: {data.type}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Bar dataKey="confidence" fill="#3b82f6" name="Confidence %" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ResultsChart;
