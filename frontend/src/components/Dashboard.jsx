import InputForm from './InputForm';
import PredictionCards from './PredictionCards';
import ChartSection from './ChartSection';

function Dashboard({ prediction, userData, onPredict }) {
  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>AI Fitness Dashboard</h1>
          <p className="subtitle">Track your body metrics and predict progress with ML</p>
        </div>
      </div>

      <div className="dashboard-content">
        <InputForm onPredict={onPredict} />
        
        {prediction && (
          <PredictionCards prediction={prediction} userData={userData} />
        )}
        
        <ChartSection prediction={prediction} userData={userData} />
      </div>
    </main>
  );
}

export default Dashboard;
