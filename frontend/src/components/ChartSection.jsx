import { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';

function ChartSection({ prediction, userData }) {
  const chartData = useMemo(() => {
    if (!prediction || !userData) return [];

    const currentWeight = Number(userData.weight);
    const predictedWeight = Number(prediction.predicted_weight);
    const goalWeight = Number(userData.goal_weight);

    if (!Number.isFinite(currentWeight) || !Number.isFinite(predictedWeight) || !Number.isFinite(goalWeight)) return [];

    const data = [];
    for (let day = 0; day <= 30; day += 5) {
      const progress = day / 30;
      data.push({
        day: `Day ${day}`,
        weight: Number((currentWeight + (predictedWeight - currentWeight) * progress).toFixed(2)),
        goal: goalWeight,
      });
    }

    return data;
  }, [prediction, userData]);

  if (!prediction || chartData.length === 0) {
    return (
      <div className="chart-section">
        <h2 className="section-title">
          <span className="title-icon">📈</span>
          Weight Prediction Chart
        </h2>
        <div className="chart-placeholder">
          <div className="placeholder-icon">📊</div>
          <p>Enter your details and get predictions to see the chart</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-section fade-card">
      <h2 className="section-title">
        <span className="title-icon">📈</span>
        Weight Prediction Chart
      </h2>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="weightGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="goalGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis 
              dataKey="day" 
              stroke="#94a3b8" 
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />
            <YAxis 
              stroke="#94a3b8" 
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip
              formatter={(value, name) => [`${Number(value).toFixed(1)} kg`, name]}
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
              labelStyle={{ color: '#e2e8f0' }}
              itemStyle={{ color: '#22c55e' }}
            />
            <Area
              type="monotone"
              dataKey="weight"
              stroke="#22c55e"
              strokeWidth={3}
              fill="url(#weightGradient)"
              name="Predicted Weight"
              animationDuration={1500}
            />
            <Line
              type="monotone"
              dataKey="goal"
              stroke="#8b5cf6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Goal Weight"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#22c55e' }}></span>
          <span>Predicted Weight</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#8b5cf6' }}></span>
          <span>Goal Weight</span>
        </div>
      </div>
    </div>
  );
}

export default ChartSection;
