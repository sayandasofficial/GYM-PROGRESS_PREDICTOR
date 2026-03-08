import { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [userData, setUserData] = useState(null);

  const handlePredict = (predictionData, submittedData) => {
    setPrediction(predictionData);
    setUserData(submittedData);
  };

  return (
    <div className="app">
      <header className="top-nav">
        <div className="top-nav-logo">FitsAI</div>
      </header>

      <Dashboard
        prediction={prediction}
        userData={userData}
        onPredict={handlePredict}
      />
    </div>
  );
}

export default App;
