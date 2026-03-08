import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, StackingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from model_pipeline import FeatureEngineer, GenderCalibratedModel, InputAdapter, Winsorizer

try:
    from xgboost import XGBRegressor

    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False


BASE_FEATURES = [
    "age",
    "gender",
    "height",
    "weight",
    "workout_days",
    "workout_minutes",
    "calories",
    "protein",
    "sleep",
]

TARGET = "future_weight"


def load_and_prepare_dataset(path="gym_data.csv"):
    data = pd.read_csv(path)

    rename_map = {
        "daily_calories": "calories",
        "protein_intake": "protein",
        "sleep_hours": "sleep",
        "height_ft": "height",
        "weight_kg": "weight",
        "workout_duration": "workout_minutes",
    }
    data = data.rename(columns=rename_map)

    if "gender" in data.columns and data["gender"].dtype == object:
        data["gender"] = data["gender"].str.strip().str.lower().map({"male": 1, "female": 0})

    missing = [column for column in BASE_FEATURES + [TARGET] if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")

    for column in BASE_FEATURES + [TARGET]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["weight", TARGET]).reset_index(drop=True)
    delta_weight = (data[TARGET] - data["weight"]).clip(-6.0, 6.0)
    data[TARGET] = data["weight"] + delta_weight
    return data


def make_pipeline(model):
    winsor_columns = ["calories", "protein", "workout_minutes", "sleep", "weight", "height"]

    numeric_features = [
        "age",
        "height",
        "weight",
        "workout_days",
        "workout_minutes",
        "calories",
        "protein",
        "sleep",
        "bmi",
        "bmr",
        "tdee",
        "workout_volume",
        "calorie_surplus",
        "protein_per_kg",
        "training_intensity",
        "recovery_score",
        "calories_x_workout",
        "protein_x_sleep",
        "age_x_workout_days",
        "is_high_protein",
        "is_sleep_deprived",
        "is_sedentary",
    ]
    categorical_features = ["gender"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("adapter", InputAdapter(BASE_FEATURES)),
            ("winsor", Winsorizer(winsor_columns, 0.01, 0.99)),
            ("features", FeatureEngineer()),
            ("preprocess", preprocess),
            ("model", model),
        ]
    )


def print_cv_results(results):
    print("\nModel Comparison (5-fold CV)")
    print("-" * 100)
    print(f"{'Model':<20} {'MAE':>10} {'MAE_std':>10} {'RMSE':>10} {'RMSE_std':>10} {'R2':>10} {'R2_std':>10}")
    print("-" * 100)
    for name, metrics in results.items():
        print(
            f"{name:<20} "
            f"{metrics['mae']:.4f} {metrics['mae_std']:.4f} "
            f"{metrics['rmse']:.4f} {metrics['rmse_std']:.4f} "
            f"{metrics['r2']:.4f} {metrics['r2_std']:.4f}"
        )
    print("-" * 100)


def get_feature_importance(pipeline):
    preprocessor = pipeline.named_steps["preprocess"]
    model = pipeline.named_steps["model"]

    if isinstance(model, StackingRegressor):
        if hasattr(model.final_estimator_, "coef_"):
            meta_names = list(model.named_estimators_.keys())
            values = np.abs(np.ravel(model.final_estimator_.coef_))
            return pd.Series(values, index=meta_names).sort_values(ascending=False)
        return None

    if not (hasattr(model, "feature_importances_") or hasattr(model, "coef_")):
        return None

    feature_names = preprocessor.get_feature_names_out()
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    else:
        values = np.abs(np.ravel(model.coef_))

    return pd.Series(values, index=feature_names).sort_values(ascending=False)


def print_subgroup_metrics(X_test, y_test, predictions):
    eval_df = X_test.copy()
    eval_df["actual"] = y_test
    eval_df["pred"] = predictions

    print("\nSubgroup Metrics (Gender)")
    for label, name in [(1, "Male"), (0, "Female")]:
        group = eval_df[eval_df["gender"] == label]
        if len(group) == 0:
            continue
        mae = mean_absolute_error(group["actual"], group["pred"])
        rmse = np.sqrt(mean_squared_error(group["actual"], group["pred"]))
        r2 = r2_score(group["actual"], group["pred"])
        print(f"{name:<7} -> samples={len(group):4d} | MAE={mae:.4f} | RMSE={rmse:.4f} | R2={r2:.4f}")


def print_time_split_metrics(data, model):
    split_idx = int(len(data) * 0.8)
    train_seq = data.iloc[:split_idx]
    test_seq = data.iloc[split_idx:]

    X_train_seq = train_seq[BASE_FEATURES]
    y_train_seq = train_seq[TARGET]
    X_test_seq = test_seq[BASE_FEATURES]
    y_test_seq = test_seq[TARGET]

    model.fit(X_train_seq, y_train_seq)
    pred_seq = model.predict(X_test_seq)
    mae = mean_absolute_error(y_test_seq, pred_seq)
    rmse = np.sqrt(mean_squared_error(y_test_seq, pred_seq))
    r2 = r2_score(y_test_seq, pred_seq)
    print(f"\nTemporal-style Holdout -> MAE={mae:.4f}, RMSE={rmse:.4f}, R2={r2:.4f}")


def build_models():
    linear = LinearRegression()
    rf = RandomForestRegressor(random_state=42)
    gbr = GradientBoostingRegressor(random_state=42)

    estimators = [("linear", linear), ("rf", rf), ("gbr", gbr)]

    models = {
        "LinearRegression": linear,
        "RandomForest": rf,
        "GradientBoosting": gbr,
        "StackingEnsemble": StackingRegressor(
            estimators=estimators,
            final_estimator=Ridge(alpha=1.0),
            cv=5,
            n_jobs=-1,
            passthrough=False,
        ),
    }

    if HAS_XGBOOST:
        xgb = XGBRegressor(
            random_state=42,
            objective="reg:squarederror",
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
        )
        models["XGBoost"] = xgb
    else:
        print("XGBoost unavailable. Install libomp and xgboost to include it.")

    return models


def get_param_grids():
    return {
        "LinearRegression": {},
        "RandomForest": {
            "model__n_estimators": [300, 600],
            "model__max_depth": [None, 10, 18],
            "model__min_samples_split": [2, 5],
            "model__min_samples_leaf": [1, 2],
        },
        "GradientBoosting": {
            "model__n_estimators": [250, 450],
            "model__learning_rate": [0.03, 0.05, 0.08],
            "model__max_depth": [2, 3, 4],
            "model__subsample": [0.8, 1.0],
        },
        "StackingEnsemble": {
            "model__final_estimator__alpha": [0.1, 1.0, 5.0, 10.0],
        },
        "XGBoost": {
            "model__n_estimators": [300, 500],
            "model__learning_rate": [0.03, 0.05, 0.08],
            "model__max_depth": [3, 4, 6],
            "model__subsample": [0.8, 1.0],
            "model__colsample_bytree": [0.8, 1.0],
        },
    }


def main():
    data = load_and_prepare_dataset("gym_data.csv")
    X = data[BASE_FEATURES]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = build_models()
    param_grids = get_param_grids()

    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    cv_results = {}
    for name, model in models.items():
        pipeline = make_pipeline(model)
        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=5,
            scoring=scoring,
            n_jobs=-1,
        )
        cv_results[name] = {
            "mae": -np.mean(scores["test_mae"]),
            "mae_std": np.std(-scores["test_mae"]),
            "rmse": -np.mean(scores["test_rmse"]),
            "rmse_std": np.std(-scores["test_rmse"]),
            "r2": np.mean(scores["test_r2"]),
            "r2_std": np.std(scores["test_r2"]),
        }

    print_cv_results(cv_results)
    best_model_name = min(cv_results, key=lambda key: cv_results[key]["rmse"])
    print(f"\nBest model from CV: {best_model_name}")

    best_pipeline = make_pipeline(models[best_model_name])
    grid = GridSearchCV(
        estimator=best_pipeline,
        param_grid=param_grids[best_model_name],
        scoring="neg_root_mean_squared_error",
        cv=5,
        n_jobs=-1,
        verbose=1,
    )
    grid.fit(X_train, y_train)
    trained_model = grid.best_estimator_
    calibrated_model = GenderCalibratedModel(
        base_model=trained_model,
        base_features=BASE_FEATURES,
        gender_column="gender",
        strength=0.75,
    )
    calibrated_model.fit(X_train, y_train)

    predictions = calibrated_model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    print("\nFinal Evaluation (Holdout Test Set)")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    print(f"Best Params: {grid.best_params_}")

    print_subgroup_metrics(X_test, y_test, predictions)
    print_time_split_metrics(data, calibrated_model)

    importance = get_feature_importance(trained_model)
    if importance is not None:
        print("\nTop Feature Importance")
        print(importance.head(15).to_string())
    else:
        print("\nFeature importance unavailable for selected model.")

    model_path = Path("model.pkl")
    with model_path.open("wb") as file:
        pickle.dump(calibrated_model, file)

    print(f"\nSaved best model to {model_path.resolve()}")
    print("Model remains API-compatible with input order:")
    print(BASE_FEATURES)


if __name__ == "__main__":
    main()
