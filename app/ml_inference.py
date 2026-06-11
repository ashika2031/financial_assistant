"""Local ML inference — loads saved .pkl models and runs predictions.

Falls back to SageMaker endpoints when configured (via cloud_stubs.SageMakerClient).
"""
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.cloud_stubs import SageMakerClient

_MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
_sagemaker = SageMakerClient()

# ── lazy-loaded model cache ───────────────────────────────────────────────────
_rf_model     = None
_rf_scaler    = None
_rf_features  = None
_lr_model     = None
_lr_scaler    = None
_lr_encoders  = None
_lr_features  = None
_lr_target_enc = None
_metrics      = None


def _load_rf():
    global _rf_model, _rf_scaler, _rf_features
    if _rf_model is None:
        with open(_MODEL_DIR / "random_forest_regressor.pkl", "rb") as f:
            _rf_model = pickle.load(f)
        with open(_MODEL_DIR / "rf_scaler.pkl", "rb") as f:
            _rf_scaler = pickle.load(f)
        with open(_MODEL_DIR / "rf_feature_names.json") as f:
            _rf_features = json.load(f)


def _load_lr():
    global _lr_model, _lr_scaler, _lr_encoders, _lr_features, _lr_target_enc
    if _lr_model is None:
        with open(_MODEL_DIR / "logistic_regression_classifier.pkl", "rb") as f:
            _lr_model = pickle.load(f)
        with open(_MODEL_DIR / "lr_scaler.pkl", "rb") as f:
            _lr_scaler = pickle.load(f)
        with open(_MODEL_DIR / "lr_label_encoders.pkl", "rb") as f:
            _lr_encoders = pickle.load(f)
        with open(_MODEL_DIR / "lr_feature_names.json") as f:
            _lr_features = json.load(f)
        with open(_MODEL_DIR / "lr_target_encoder.pkl", "rb") as f:
            _lr_target_enc = pickle.load(f)


def get_metrics() -> Dict:
    global _metrics
    if _metrics is None:
        try:
            with open(_MODEL_DIR / "model_metrics.json") as f:
                _metrics = json.load(f)
        except Exception:
            _metrics = {}
    return _metrics


def models_ready() -> bool:
    return (
        (_MODEL_DIR / "random_forest_regressor.pkl").exists()
        and (_MODEL_DIR / "rf_scaler.pkl").exists()
        and (_MODEL_DIR / "logistic_regression_classifier.pkl").exists()
        and (_MODEL_DIR / "lr_scaler.pkl").exists()
    )


# ── Regression ─────────────────────────────────────────────────────────────────

def predict_housing_value(features: Dict[str, float]) -> Dict[str, Any]:
    """Predict median house value (100k units) from CA Housing features.

    Args:
        features: dict with keys matching rf_feature_names.json
    Returns:
        {prediction: float, unit: str, source: str}
    """
    # Try SageMaker first
    if _sagemaker.configured:
        _load_rf()
        vals = [features.get(f, 0.0) for f in _rf_features]
        result = _sagemaker.predict_regression(vals)
        if result is not None:
            return {"prediction": result, "unit": "$100k", "source": "SageMaker"}

    # Local fallback
    try:
        _load_rf()
        vals = [[features.get(f, 0.0) for f in _rf_features]]
        scaled = _rf_scaler.transform(vals)
        pred = float(_rf_model.predict(scaled)[0])
        return {"prediction": round(pred, 4), "unit": "$100k", "source": "Local model"}
    except Exception as e:
        return {"error": str(e), "prediction": None, "source": "error"}


def get_rf_feature_names() -> List[str]:
    _load_rf()
    return _rf_features or []


def get_rf_feature_descriptions() -> Dict[str, str]:
    return {
        "MedInc":     "Median income in block group (tens of thousands $)",
        "HouseAge":   "Median house age in block group (years)",
        "AveRooms":   "Average number of rooms per household",
        "AveBedrms":  "Average number of bedrooms per household",
        "Population": "Block group population",
        "AveOccup":   "Average number of household members",
        "Latitude":   "Block group latitude",
        "Longitude":  "Block group longitude",
    }


# ── Classification ─────────────────────────────────────────────────────────────

def predict_subscription(features: Dict) -> Dict[str, Any]:
    """Predict whether a bank customer will subscribe (yes/no).

    Args:
        features: dict with raw (pre-encoding) feature values
    Returns:
        {prediction: str, probability: float, source: str}
    """
    # Try SageMaker first
    if _sagemaker.configured:
        _load_lr()
        encoded = _encode_lr_features(features)
        if encoded:
            result = _sagemaker.predict_classification(encoded)
            if result:
                label = _lr_target_enc.inverse_transform([result["prediction"]])[0]
                return {"prediction": label, "probability": max(result["probability"]), "source": "SageMaker"}

    # Local fallback
    try:
        _load_lr()
        encoded = _encode_lr_features(features)
        if not encoded:
            return {"error": "feature encoding failed", "prediction": None}
        import numpy as np
        X = np.array([encoded])
        X_s = _lr_scaler.transform(X)
        pred = int(_lr_model.predict(X_s)[0])
        prob = float(_lr_model.predict_proba(X_s)[0][pred])
        label = _lr_target_enc.inverse_transform([pred])[0]
        return {"prediction": label, "probability": round(prob, 4), "source": "Local model"}
    except Exception as e:
        return {"error": str(e), "prediction": None, "source": "error"}


def _encode_lr_features(features: Dict) -> Optional[List[float]]:
    try:
        _load_lr()
        row = []
        for col in _lr_features:
            val = features.get(col, 0)
            if col in _lr_encoders:
                le = _lr_encoders[col]
                str_val = str(val)
                if str_val in le.classes_:
                    val = int(le.transform([str_val])[0])
                else:
                    val = 0
            row.append(float(val))
        return row
    except Exception:
        return None


def get_lr_feature_names() -> List[str]:
    _load_lr()
    return _lr_features or []


def get_lr_categorical_options() -> Dict[str, List[str]]:
    _load_lr()
    if not _lr_encoders:
        return {}
    return {col: list(le.classes_) for col, le in _lr_encoders.items()}
