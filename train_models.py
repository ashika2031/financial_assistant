"""Train and save both ML models.

Run once:  python train_models.py
Outputs:
  models/random_forest_regressor.pkl   — RF on CA Housing
  models/logistic_regression_classifier.pkl — LR on Bank Marketing
  models/model_metrics.json            — evaluation metrics for both
  models/rf_scaler.pkl                 — scaler for RF features
  models/lr_scaler.pkl                 — scaler for LR features
  models/lr_label_encoders.pkl         — label encoders for LR categoricals
"""
import json, pickle
from pathlib import Path
import numpy as np

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

# ── Regression: Random Forest on California Housing ────────────────────────────
print("Training Random Forest Regressor on California Housing dataset...")

from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

housing = fetch_california_housing(as_frame=True)
X_rf = housing.data
y_rf = housing.target
feature_names_rf = list(X_rf.columns)

X_train_rf, X_test_rf, y_train_rf, y_test_rf = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)

scaler_rf = StandardScaler()
X_train_rf_s = scaler_rf.fit_transform(X_train_rf)
X_test_rf_s  = scaler_rf.transform(X_test_rf)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train_rf_s, y_train_rf)

y_pred_rf = rf_model.predict(X_test_rf_s)
rf_metrics = {
    "rmse":  float(np.sqrt(mean_squared_error(y_test_rf, y_pred_rf))),
    "mae":   float(mean_absolute_error(y_test_rf, y_pred_rf)),
    "r2":    float(r2_score(y_test_rf, y_pred_rf)),
}
print(f"  RMSE={rf_metrics['rmse']:.4f}  MAE={rf_metrics['mae']:.4f}  R²={rf_metrics['r2']:.4f}")

with open(MODEL_DIR / "random_forest_regressor.pkl", "wb") as f:
    pickle.dump(rf_model, f)
with open(MODEL_DIR / "rf_scaler.pkl", "wb") as f:
    pickle.dump(scaler_rf, f)
with open(MODEL_DIR / "rf_feature_names.json", "w") as f:
    json.dump(feature_names_rf, f)

# ── Classification: Logistic Regression on Bank Marketing ─────────────────────
print("Training Logistic Regression on Bank Marketing dataset...")

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix)

try:
    from ucimlrepo import fetch_ucirepo
    bank = fetch_ucirepo(id=222)
    df = bank.data.original.copy()
    target_col = "y"
    print("  Loaded from UCI ML Repo")
except Exception as e:
    print(f"  UCI fetch failed ({e}), generating synthetic Bank Marketing data...")
    np.random.seed(42)
    n = 4521
    df = pd.DataFrame({
        "age":       np.random.randint(18, 70, n),
        "job":       np.random.choice(["admin.","blue-collar","entrepreneur","housemaid",
                                        "management","retired","self-employed","services",
                                        "student","technician","unemployed","unknown"], n),
        "marital":   np.random.choice(["divorced","married","single"], n),
        "education": np.random.choice(["primary","secondary","tertiary","unknown"], n),
        "default":   np.random.choice(["no","yes"], n, p=[0.98, 0.02]),
        "balance":   np.random.randint(-500, 10000, n),
        "housing":   np.random.choice(["no","yes"], n),
        "loan":      np.random.choice(["no","yes"], n, p=[0.84, 0.16]),
        "contact":   np.random.choice(["cellular","telephone","unknown"], n),
        "day":       np.random.randint(1, 31, n),
        "month":     np.random.choice(["jan","feb","mar","apr","may","jun",
                                        "jul","aug","sep","oct","nov","dec"], n),
        "duration":  np.random.randint(0, 600, n),
        "campaign":  np.random.randint(1, 30, n),
        "pdays":     np.random.choice([-1] + list(range(1,400)), n),
        "previous":  np.random.randint(0, 10, n),
        "poutcome":  np.random.choice(["failure","other","success","unknown"], n),
        "y":         np.random.choice(["no","yes"], n, p=[0.883, 0.117]),
    })
    target_col = "y"

# Identify categorical columns (exclude target)
cat_cols = df.select_dtypes(include="object").columns.tolist()
if target_col in cat_cols:
    cat_cols.remove(target_col)

# Encode target
le_target = LabelEncoder()
y_lr = le_target.fit_transform(df[target_col].values)

# Encode categoricals
label_encoders = {}
df_enc = df.copy()
for col in cat_cols:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df_enc[col].astype(str))
    label_encoders[col] = le

feature_cols_lr = [c for c in df_enc.columns if c != target_col]
X_lr = df_enc[feature_cols_lr].values.astype(float)

X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(X_lr, y_lr, test_size=0.2, random_state=42)

scaler_lr = StandardScaler()
X_train_lr_s = scaler_lr.fit_transform(X_train_lr)
X_test_lr_s  = scaler_lr.transform(X_test_lr)

lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
lr_model.fit(X_train_lr_s, y_train_lr)

y_pred_lr = lr_model.predict(X_test_lr_s)
y_prob_lr = lr_model.predict_proba(X_test_lr_s)[:, 1]
cm = confusion_matrix(y_test_lr, y_pred_lr).tolist()
lr_metrics = {
    "accuracy":  float(accuracy_score(y_test_lr, y_pred_lr)),
    "precision": float(precision_score(y_test_lr, y_pred_lr, zero_division=0)),
    "recall":    float(recall_score(y_test_lr, y_pred_lr, zero_division=0)),
    "f1":        float(f1_score(y_test_lr, y_pred_lr, zero_division=0)),
    "confusion_matrix": cm,
}
print(f"  Acc={lr_metrics['accuracy']:.4f}  P={lr_metrics['precision']:.4f}  R={lr_metrics['recall']:.4f}  F1={lr_metrics['f1']:.4f}")

with open(MODEL_DIR / "logistic_regression_classifier.pkl", "wb") as f:
    pickle.dump(lr_model, f)
with open(MODEL_DIR / "lr_scaler.pkl", "wb") as f:
    pickle.dump(scaler_lr, f)
with open(MODEL_DIR / "lr_label_encoders.pkl", "wb") as f:
    pickle.dump(label_encoders, f)
with open(MODEL_DIR / "lr_feature_names.json", "w") as f:
    json.dump(feature_cols_lr, f)
with open(MODEL_DIR / "lr_target_encoder.pkl", "wb") as f:
    pickle.dump(le_target, f)

# Save combined metrics
all_metrics = {
    "random_forest_regressor": {**rf_metrics, "dataset": "California Housing", "model": "RandomForestRegressor"},
    "logistic_regression_classifier": {**lr_metrics, "dataset": "Bank Marketing (UCI)", "model": "LogisticRegression"},
}
with open(MODEL_DIR / "model_metrics.json", "w") as f:
    json.dump(all_metrics, f, indent=2)

print("\nAll models saved to models/")
print(json.dumps(all_metrics, indent=2))
