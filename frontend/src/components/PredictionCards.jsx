function PredictionCards({ prediction, userData }) {
  if (!prediction) return null;

  const bmi = Number(prediction.bmi ?? 0);
  const predictedWeight = Number(prediction.predicted_weight ?? 0);
  const maintenanceCalories = Number(prediction.maintenance_calories ?? 0);
  const goalProgress = Number(prediction.goal_progress ?? 0);

  const getBMICategory = (value) => {
    if (value < 18.5) return { category: 'Underweight', color: '#fbbf24' };
    if (value < 25) return { category: 'Normal', color: '#22c55e' };
    if (value < 30) return { category: 'Overweight', color: '#f97316' };
    return { category: 'Obese', color: '#ef4444' };
  };

  const bmiInfo = getBMICategory(bmi);

  const cards = [
    {
      id: 'bmi',
      icon: '⚖️',
      title: 'BMI',
      value: bmi.toFixed(1),
      subtitle: bmiInfo.category,
      color: bmiInfo.color,
    },
    {
      id: 'weight',
      icon: '📊',
      title: 'Predicted Weight',
      value: `${predictedWeight.toFixed(1)} kg`,
      subtitle: 'in 30 days',
      color: '#8b5cf6',
    },
    {
      id: 'calories',
      icon: '🔥',
      title: 'Maintenance Calories',
      value: `${maintenanceCalories.toFixed(0)} kcal`,
      subtitle: 'per day',
      color: '#f59e0b',
    },
  ];

  return (
    <div className="prediction-cards">
      <div className="cards-grid">
        {cards.map((card) => (
          <div
            key={card.id}
            className="prediction-card fade-card"
            style={{ '--card-color': card.color }}
          >
            <div className="card-header">
              <span className="card-icon">{card.icon}</span>
              <span className="card-title">{card.title}</span>
            </div>
            <div className="card-value" style={{ color: card.color }}>
              {card.value}
            </div>
            <div className="card-subtitle">{card.subtitle}</div>
          </div>
        ))}
      </div>

      <div className="goal-progress fade-card">
          <div className="progress-header">
            <h3>
              <span className="progress-icon">🎯</span>
              Goal Progress
            </h3>
            <span className="progress-percentage">{goalProgress.toFixed(1)}%</span>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar" style={{ width: `${Math.max(0, Math.min(goalProgress, 100))}%` }}>
              <div className="progress-glow"></div>
            </div>
          </div>
          <div className="progress-details">
            <span>Current: {Number(userData?.weight ?? 0).toFixed(1)} kg</span>
            <span>Goal: {Number(userData?.goal_weight ?? 0).toFixed(1)} kg</span>
          </div>
      </div>
    </div>
  );
}

export default PredictionCards;
