import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin


class InputAdapter(BaseEstimator, TransformerMixin):
    def __init__(self, base_features):
        self.base_features = base_features

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            return X[self.base_features].copy()
        return pd.DataFrame(X, columns=self.base_features)


class Winsorizer(BaseEstimator, TransformerMixin):
    def __init__(self, columns, lower_quantile=0.01, upper_quantile=0.99):
        self.columns = columns
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.lower_bounds_ = {}
        self.upper_bounds_ = {}

    def fit(self, X, y=None):
        data = X.copy()
        for column in self.columns:
            series = pd.to_numeric(data[column], errors="coerce")
            self.lower_bounds_[column] = float(series.quantile(self.lower_quantile))
            self.upper_bounds_[column] = float(series.quantile(self.upper_quantile))
        return self

    def transform(self, X):
        data = X.copy()
        for column in self.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce").clip(
                self.lower_bounds_[column],
                self.upper_bounds_[column],
            )
        return data


class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        data = X.copy()

        age = pd.to_numeric(data["age"], errors="coerce")
        gender = pd.to_numeric(data["gender"], errors="coerce").fillna(1)
        height = pd.to_numeric(data["height"], errors="coerce").clip(lower=1.2)
        weight = pd.to_numeric(data["weight"], errors="coerce")
        workout_days = pd.to_numeric(data["workout_days"], errors="coerce")
        workout_minutes = pd.to_numeric(data["workout_minutes"], errors="coerce")
        calories = pd.to_numeric(data["calories"], errors="coerce")
        protein = pd.to_numeric(data["protein"], errors="coerce")
        sleep = pd.to_numeric(data["sleep"], errors="coerce")

        bmi = weight / (height**2)
        height_cm = height * 100
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + np.where(gender == 1, 5, -161)
        activity_factor = 1.2 + np.minimum((workout_days * workout_minutes) / 1700, 0.5)
        tdee = bmr * activity_factor
        workout_volume = workout_days * workout_minutes
        calorie_surplus = calories - tdee
        protein_per_kg = protein / np.maximum(weight, 1)
        training_intensity = workout_minutes / np.maximum(workout_days, 1)
        recovery_score = (sleep * 0.7) + (protein_per_kg * 1.1) - (training_intensity / 120)

        data["bmi"] = bmi
        data["bmr"] = bmr
        data["tdee"] = tdee
        data["workout_volume"] = workout_volume
        data["calorie_surplus"] = calorie_surplus
        data["protein_per_kg"] = protein_per_kg
        data["training_intensity"] = training_intensity
        data["recovery_score"] = recovery_score

        data["calories_x_workout"] = calories * workout_volume
        data["protein_x_sleep"] = protein * sleep
        data["age_x_workout_days"] = age * workout_days

        data["is_high_protein"] = (protein_per_kg >= 1.6).astype(int)
        data["is_sleep_deprived"] = (sleep < 6.5).astype(int)
        data["is_sedentary"] = (workout_days <= 1).astype(int)
        return data


class GenderCalibratedModel(BaseEstimator, RegressorMixin):
    def __init__(self, base_model, base_features, gender_column="gender", strength=0.8):
        self.base_model = base_model
        self.base_features = base_features
        self.gender_column = gender_column
        self.strength = strength
        self.calibration_ = {}

    def fit(self, X, y):
        self.base_model.fit(X, y)

        data = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=self.base_features)
        preds = np.asarray(self.base_model.predict(data), dtype=float)
        actual = np.asarray(y, dtype=float)
        gender_values = pd.to_numeric(data[self.gender_column], errors="coerce").fillna(1).astype(int)

        self.calibration_ = {}
        for gender_value in [0, 1]:
            mask = gender_values == gender_value
            if int(mask.sum()) < 10:
                self.calibration_[gender_value] = (1.0, 0.0)
                continue

            pred_group = preds[mask]
            actual_group = actual[mask]

            slope, intercept = np.polyfit(pred_group, actual_group, 1)
            slope = (1 - self.strength) + (self.strength * float(slope))
            intercept = self.strength * float(intercept)
            self.calibration_[gender_value] = (slope, intercept)

        return self

    def predict(self, X):
        data = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=self.base_features)
        raw_pred = np.asarray(self.base_model.predict(data), dtype=float)
        gender_values = pd.to_numeric(data[self.gender_column], errors="coerce").fillna(1).astype(int).to_numpy()

        calibrated = raw_pred.copy()
        for gender_value, (slope, intercept) in self.calibration_.items():
            mask = gender_values == gender_value
            calibrated[mask] = (raw_pred[mask] * slope) + intercept

        return calibrated
