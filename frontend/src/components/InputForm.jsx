import { useState } from 'react';
import { getApiErrorMessage, postWithFallback } from '../api';

function InputForm({ onPredict }) {
  const [formData, setFormData] = useState({
    age: '',
    gender: '1',
    height: '',
    weight: '',
    workout_days: '',
    workout_minutes: '',
    calories: '',
    protein: '',
    sleep: '',
    goal_weight: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const numericFields = [
    'age',
    'height',
    'weight',
    'workout_days',
    'workout_minutes',
    'calories',
    'protein',
    'sleep',
    'goal_weight',
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        age: parseInt(formData.age),
        gender: Number(formData.gender),
        height: parseFloat(formData.height) * 0.3048,
        weight: parseFloat(formData.weight),
        workout_days: parseInt(formData.workout_days),
        workout_minutes: parseInt(formData.workout_minutes),
        calories: parseInt(formData.calories),
        protein: parseInt(formData.protein),
        sleep: parseFloat(formData.sleep),
        goal_weight: parseFloat(formData.goal_weight),
      };

      if (numericFields.some((field) => !Number.isFinite(payload[field]))) {
        throw new Error('Please enter valid numeric values in all fields.');
      }

      const response = await postWithFallback('/predict', payload);
      onPredict(response.data, payload);
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="input-form-container">
      <h2 className="section-title">
        <span className="title-icon">📝</span>
        User Input Form
      </h2>
      
      <form onSubmit={handleSubmit} className="input-form">
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="age">Age</label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="25"
              required
              min="15"
              max="100"
            />
          </div>

          <div className="form-group">
            <label htmlFor="gender">Gender</label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              required
            >
              <option value="1">Male</option>
              <option value="0">Female</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="height">Height (ft)</label>
            <input
              type="number"
              id="height"
              name="height"
              value={formData.height}
              onChange={handleChange}
              placeholder="5.9"
              required
              step="0.01"
              min="3"
              max="8"
            />
          </div>

          <div className="form-group">
            <label htmlFor="weight">Current Weight (kg)</label>
            <input
              type="number"
              id="weight"
              name="weight"
              value={formData.weight}
              onChange={handleChange}
              placeholder="70"
              required
              step="0.1"
              min="30"
              max="300"
            />
          </div>

          <div className="form-group">
            <label htmlFor="workout_days">Workout Days/Week</label>
            <input
              type="number"
              id="workout_days"
              name="workout_days"
              value={formData.workout_days}
              onChange={handleChange}
              placeholder="4"
              required
              min="0"
              max="7"
            />
          </div>

          <div className="form-group">
            <label htmlFor="workout_minutes">Workout Minutes/Day</label>
            <input
              type="number"
              id="workout_minutes"
              name="workout_minutes"
              value={formData.workout_minutes}
              onChange={handleChange}
              placeholder="45"
              required
              min="0"
              max="300"
            />
          </div>

          <div className="form-group">
            <label htmlFor="calories">Daily Calories</label>
            <input
              type="number"
              id="calories"
              name="calories"
              value={formData.calories}
              onChange={handleChange}
              placeholder="2000"
              required
              min="500"
              max="10000"
            />
          </div>

          <div className="form-group">
            <label htmlFor="protein">Protein Intake (g)</label>
            <input
              type="number"
              id="protein"
              name="protein"
              value={formData.protein}
              onChange={handleChange}
              placeholder="150"
              required
              min="0"
              max="500"
            />
          </div>

          <div className="form-group">
            <label htmlFor="sleep">Sleep Hours</label>
            <input
              type="number"
              id="sleep"
              name="sleep"
              value={formData.sleep}
              onChange={handleChange}
              placeholder="7"
              required
              step="0.5"
              min="0"
              max="24"
            />
          </div>

          <div className="form-group">
            <label htmlFor="goal_weight">Goal Weight (kg)</label>
            <input
              type="number"
              id="goal_weight"
              name="goal_weight"
              value={formData.goal_weight}
              onChange={handleChange}
              placeholder="65"
              required
              step="0.1"
              min="30"
              max="300"
            />
          </div>
        </div>

        {error && <div className="form-error">{error}</div>}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <span className="loading-spinner"></span>
              Predicting...
            </>
          ) : (
            <>
              <span className="btn-icon">🔮</span>
              Predict Progress
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default InputForm;
