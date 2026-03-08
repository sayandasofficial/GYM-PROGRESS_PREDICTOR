import numpy as np
import pandas as pd

np.random.seed(42)

rows = 5000

age = np.random.normal(30, 9, rows).clip(18, 60).round().astype(int)
gender = np.random.choice([1, 0], rows, p=[0.55, 0.45])

height_m = np.where(
    gender == 1,
    np.random.normal(1.76, 0.07, rows),
    np.random.normal(1.63, 0.06, rows),
).clip(1.45, 2.05)
height_m = np.round(height_m, 3)

bmi_seed = np.random.normal(24.2, 3.8, rows).clip(18, 35)
weight_kg = bmi_seed * (height_m**2)
weight_kg = np.round(weight_kg + np.random.normal(0, 2.2, rows), 1).clip(45, 150)

workout_days = np.random.randint(0, 7, rows)
workout_minutes = np.round(np.random.normal(55, 20, rows).clip(0, 140)).astype(int)

height_cm = height_m * 100
bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + np.where(gender == 1, 5, -161)
activity_factor = 1.2 + np.minimum((workout_days * workout_minutes) / 1700, 0.5)
tdee = bmr * activity_factor

daily_calories = np.round(
    tdee + np.random.normal(0, 280, rows) + np.random.normal(0, 120, rows)
).clip(1300, 4200)

protein_intake = np.round(
    (weight_kg * np.random.normal(1.5, 0.35, rows)) + (workout_days * 3)
).clip(45, 260)

sleep_hours = np.round(np.random.normal(7.1, 1.1, rows).clip(4.0, 9.8), 1)

monthly_calorie_effect = ((daily_calories - tdee) * 30) / 7700
training_effect = (
    (workout_days * workout_minutes / 900)
    + (protein_intake / 180)
    + ((sleep_hours - 6.5) * 0.25)
)
sex_factor = np.where(gender == 1, 0.15, 0.0)
noise = np.random.normal(0, 0.5, rows)

future_weight = weight_kg + monthly_calorie_effect + training_effect + sex_factor + noise
future_weight = np.round(np.clip(future_weight, 40, 180), 2)

data = pd.DataFrame(
    {
        "age": age,
        "gender": gender,
        "height": height_m,
        "weight": weight_kg,
        "workout_days": workout_days,
        "workout_minutes": workout_minutes,
        "daily_calories": daily_calories,
        "protein_intake": protein_intake,
        "sleep_hours": sleep_hours,
        "future_weight": future_weight,
    }
)

data.to_csv("gym_data.csv", index=False)
print(f"Dataset generated successfully with {len(data)} rows")
