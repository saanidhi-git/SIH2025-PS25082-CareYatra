# train_insurance_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# 1) Load data
df = pd.read_csv("file.csv")   # download from Kaggle and put here
print(df.shape)
print(df.head())

# 2) Features / target
X = df.drop(columns=["charges"])
y = df["charges"]

# 3) Column groups
num_cols = ["age", "bmi", "children"]
cat_cols = ["sex", "smoker", "region"]

# 4) Preprocessing
num_transformer = Pipeline([
    ("scaler", StandardScaler())
])
# Use sparse=False to get dense arrays; if you get a DeprecationWarning, replace with sparse_output=False for newer sklearn
cat_transformer = OneHotEncoder(handle_unknown="ignore", sparse=False)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", num_transformer, num_cols),
        ("cat", cat_transformer, cat_cols),
    ],
    remainder="drop",
)

# 5) Full pipeline: preprocessor + model
pipe = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(random_state=42))
])

# 6) Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 7) (Optional) small grid search for decent hyperparams
param_grid = {
    "model__n_estimators": [100, 200],
    "model__max_depth": [None, 10, 20],
}
grid = GridSearchCV(pipe, param_grid, cv=4, n_jobs=-1, scoring="neg_mean_absolute_error", verbose=1)
grid.fit(X_train, y_train)

best = grid.best_estimator_
print("Best params:", grid.best_params_)

# 8) Evaluate
y_pred = best.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)
print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.3f}")

# 9) Save pipeline (contains preprocessor + model)
joblib.dump(best, "insurance_pipeline.joblib")
print("Saved pipeline to insurance_pipeline.joblib")
