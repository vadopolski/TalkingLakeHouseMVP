import React from 'react';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BarChartProps {
  data: any[];
  title?: string;
  xKey?: string;
  yKey?: string;
  color?: string;
}

const BarChart: React.FC<BarChartProps> = ({
  data,
  title,
  xKey = 'date',
  yKey = 'revenue',
  color = '#3498db'
}) => {
  if (!data || data.length === 0) {
    return (
      <div style={styles.emptyState}>
        <p>No data available for chart</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {title && <h3 style={styles.title}>{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <RechartsBarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip
            formatter={(value: any) => {
              if (typeof value === 'number') {
                // Format as currency if key contains 'revenue'
                if (yKey.toLowerCase().includes('revenue')) {
                  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                }
                return value.toLocaleString();
              }
              return value;
            }}
          />
          <Legend />
          <Bar dataKey={yKey} fill={color} />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginTop: '16px'
  },
  title: {
    margin: '0 0 20px 0',
    fontSize: '18px',
    fontWeight: 600,
    color: '#2c3e50'
  },
  emptyState: {
    padding: '40px',
    textAlign: 'center' as const,
    color: '#95a5a6',
    backgroundColor: '#ecf0f1',
    borderRadius: '8px',
    marginTop: '16px'
  }
};

export default BarChart;
