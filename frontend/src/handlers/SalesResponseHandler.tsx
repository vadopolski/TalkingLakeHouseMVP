import React from 'react';
import BarChart from '../components/charts/BarChart';
import LineChart from '../components/charts/LineChart';

interface SalesResponseHandlerProps {
  textResponse: string;
  chartData?: {
    type: string;
    data: any[];
    labels?: string[];
    datasets?: any[];
  };
  citation?: string;
}

const SalesResponseHandler: React.FC<SalesResponseHandlerProps> = ({
  textResponse,
  chartData,
  citation
}) => {
  const renderChart = () => {
    if (!chartData || !chartData.data || chartData.data.length === 0) {
      return null;
    }

    const { type, data } = chartData;

    switch (type) {
      case 'bar':
        return (
          <BarChart
            data={data}
            title="Sales Data"
            xKey="date"
            yKey="revenue"
            color="#3498db"
          />
        );

      case 'line':
        return (
          <LineChart
            data={data}
            title="Sales Trend"
            xKey="date"
            yKey="revenue"
            color="#2ecc71"
          />
        );

      default:
        // Fallback to bar chart
        return (
          <BarChart
            data={data}
            title="Sales Data"
            color="#3498db"
          />
        );
    }
  };

  return (
    <div style={styles.container}>
      {/* Text Response */}
      <div style={styles.textResponse}>
        <p>{textResponse}</p>
      </div>

      {/* Chart */}
      {chartData && renderChart()}

      {/* Citation */}
      {citation && (
        <div style={styles.citation}>
          <small>{citation}</small>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    width: '100%'
  },
  textResponse: {
    padding: '12px 0',
    fontSize: '15px',
    lineHeight: '1.6',
    color: '#2c3e50'
  },
  citation: {
    marginTop: '12px',
    padding: '8px 12px',
    backgroundColor: '#ecf0f1',
    borderRadius: '4px',
    fontSize: '12px',
    color: '#7f8c8d',
    borderLeft: '3px solid #3498db'
  }
};

export default SalesResponseHandler;
