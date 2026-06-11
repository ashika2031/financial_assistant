"""ML Predictions — regression and classification dashboards."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

st.set_page_config(page_title="ML Predictions · Prologis AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card, status_badge, page_footer, sample_disclaimer
apply_global_styles()

from app import ml_inference
from app.cloud_stubs import SageMakerClient
import pandas as pd

_sm = SageMakerClient()
sm_st = _sm.status()

hero_card(
    "ML Predictions",
    "Random Forest regression · Logistic Regression classification · Local & SageMaker inference",
    "🤖",
)

# ── Engine status ─────────────────────────────────────────────────────────────
status_badge("SageMaker" if sm_st["configured"] else "Local scikit-learn models", sm_st["configured"])

if not sm_st["configured"]:
    st.markdown(
        f"<div style='background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.17);"
        f"border-radius:8px;padding:0.55rem 1rem;font-size:0.78rem;color:#7dd3fc;margin-bottom:1rem;'>"
        f"💻 Running local scikit-learn models &nbsp;·&nbsp; {sm_st['note']}"
        f"</div>",
        unsafe_allow_html=True,
    )

if not ml_inference.models_ready():
    st.error("ML models not found. Run `python train_models.py` first.")
    st.code("python train_models.py")
    st.stop()

metrics = ml_inference.get_metrics()
rf_m = metrics.get("random_forest_regressor", {})
lr_m = metrics.get("logistic_regression_classifier", {})

# ── Model performance row ─────────────────────────────────────────────────────
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.75rem;'>Model Performance</div>",
            unsafe_allow_html=True)

col_rf, col_lr = st.columns(2)

with col_rf:
    st.markdown(
        "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;margin-bottom:4px;'>Random Forest Regressor</div>"
        "<div style='font-size:0.78rem;color:#475569;margin-bottom:0.7rem;'>"
        "California Housing · scikit-learn</div>",
        unsafe_allow_html=True,
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("RMSE", f"{rf_m.get('rmse', 0):.4f}")
    m2.metric("MAE",  f"{rf_m.get('mae', 0):.4f}")
    m3.metric("R²",   f"{rf_m.get('r2', 0):.4f}")

with col_lr:
    st.markdown(
        "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;margin-bottom:4px;'>Logistic Regression Classifier</div>"
        "<div style='font-size:0.78rem;color:#475569;margin-bottom:0.7rem;'>"
        "Bank Marketing · UCI ML Repository</div>",
        unsafe_allow_html=True,
    )
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Accuracy",  f"{lr_m.get('accuracy', 0):.3f}")
    m2.metric("Precision", f"{lr_m.get('precision', 0):.3f}")
    m3.metric("Recall",    f"{lr_m.get('recall', 0):.3f}")
    m4.metric("F1 Score",  f"{lr_m.get('f1', 0):.3f}")

    cm = lr_m.get("confusion_matrix")
    if cm:
        st.markdown(
            "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
            "letter-spacing:0.08em;margin-top:0.75rem;margin-bottom:0.3rem;'>Confusion Matrix</div>",
            unsafe_allow_html=True,
        )
        cm_df = pd.DataFrame(cm, index=["Actual No", "Actual Yes"], columns=["Pred No", "Pred Yes"])
        st.dataframe(cm_df, use_container_width=False)

st.divider()

# ── Prediction tabs ───────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🏠 Housing Value — Regression", "📊 Subscription — Classification"])

# ── Tab 1: Regression ─────────────────────────────────────────────────────────
with tab1:
    st.markdown(
        "<div style='font-size:0.82rem;color:#64748b;margin-bottom:1rem;'>"
        "Random Forest Regressor on California Housing dataset. "
        "Output unit = $100,000 &nbsp;(e.g. 2.5 → $250,000)."
        "</div>",
        unsafe_allow_html=True,
    )

    descs    = ml_inference.get_rf_feature_descriptions()
    rf_feats = ml_inference.get_rf_feature_names()
    defaults = {
        "MedInc": 3.87, "HouseAge": 28.0, "AveRooms": 5.43, "AveBedrms": 1.10,
        "Population": 1425.0, "AveOccup": 3.07, "Latitude": 35.63, "Longitude": -119.57,
    }

    st.markdown(
        "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;margin-bottom:0.6rem;'>Input Features</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    inputs_rf = {}
    for i, feat in enumerate(rf_feats):
        with cols[i % 4]:
            inputs_rf[feat] = st.number_input(
                feat, value=float(defaults.get(feat, 0.0)),
                help=descs.get(feat, feat), key=f"rf_{feat}",
            )

    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
    if st.button("Run Housing Value Prediction", type="primary", key="btn_rf"):
        with st.spinner("Running Random Forest inference…"):
            result = ml_inference.predict_housing_value(inputs_rf)
        if result.get("prediction") is not None:
            val = result["prediction"] * 100_000
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#0c2340,#1e293b);"
                f"border:1px solid #38bdf8;border-radius:12px;"
                f"padding:1.2rem 1.5rem;margin-top:0.75rem;box-sizing:border-box;'>"
                f"<div style='font-size:0.69rem;color:#64748b;font-weight:700;"
                f"text-transform:uppercase;letter-spacing:0.08em;'>Predicted Median House Value</div>"
                f"<div style='font-size:2.1rem;font-weight:800;color:#38bdf8;margin-top:5px;'>${val:,.0f}</div>"
                f"<div style='font-size:0.75rem;color:#475569;margin-top:4px;'>"
                f"Raw: {result['prediction']:.4f} × $100k &nbsp;·&nbsp; Source: {result['source']}"
                f"</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.error(f"Prediction failed: {result.get('error')}")

# ── Tab 2: Classification ─────────────────────────────────────────────────────
with tab2:
    st.markdown(
        "<div style='font-size:0.82rem;color:#64748b;margin-bottom:1rem;'>"
        "Logistic Regression on Bank Marketing (UCI). "
        "Predicts whether a customer will subscribe to a term deposit (yes / no)."
        "</div>",
        unsafe_allow_html=True,
    )

    cat_opts    = ml_inference.get_lr_categorical_options()
    lr_feats    = ml_inference.get_lr_feature_names()
    defaults_lr = {
        "age": 40, "balance": 1500, "day": 15, "duration": 180,
        "campaign": 2, "pdays": -1, "previous": 0,
        "job": "management", "marital": "married", "education": "tertiary",
        "default": "no", "housing": "yes", "loan": "no",
        "contact": "cellular", "month": "may", "poutcome": "unknown",
    }

    st.markdown(
        "<div style='font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;"
        "letter-spacing:0.08em;margin-bottom:0.6rem;'>Customer Features</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    inputs_lr = {}
    for i, feat in enumerate(lr_feats):
        with cols[i % 4]:
            if feat in cat_opts:
                opts = cat_opts[feat]
                dv = defaults_lr.get(feat, opts[0])
                idx = opts.index(dv) if dv in opts else 0
                inputs_lr[feat] = st.selectbox(feat, opts, index=idx, key=f"lr_{feat}")
            else:
                inputs_lr[feat] = st.number_input(
                    feat, value=float(defaults_lr.get(feat, 0)), key=f"lr_{feat}",
                )

    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
    if st.button("Run Subscription Prediction", type="primary", key="btn_lr"):
        with st.spinner("Running Logistic Regression inference…"):
            result = ml_inference.predict_subscription(inputs_lr)
        if result.get("prediction") is not None:
            pred   = result["prediction"]
            prob   = result["probability"]
            is_yes = pred == "yes"
            accent = "#4ade80" if is_yes else "#f59e0b"
            bg_c   = "rgba(74,222,128,0.07)"  if is_yes else "rgba(245,158,11,0.07)"
            bdr    = "rgba(74,222,128,0.3)"   if is_yes else "rgba(245,158,11,0.3)"
            label  = "WILL SUBSCRIBE" if is_yes else "WILL NOT SUBSCRIBE"
            st.markdown(
                f"<div style='background:{bg_c};border:1px solid {bdr};"
                f"border-radius:12px;padding:1.2rem 1.5rem;margin-top:0.75rem;box-sizing:border-box;'>"
                f"<div style='font-size:0.69rem;color:#64748b;font-weight:700;"
                f"text-transform:uppercase;letter-spacing:0.08em;'>Subscription Prediction</div>"
                f"<div style='font-size:1.9rem;font-weight:800;color:{accent};margin-top:5px;'>{label}</div>"
                f"<div style='font-size:0.83rem;color:#94a3b8;margin-top:5px;'>"
                f"Confidence: <strong style='color:{accent};'>{prob*100:.1f}%</strong>"
                f" &nbsp;·&nbsp; Source: {result['source']}"
                f"</div></div>",
                unsafe_allow_html=True,
            )
            st.progress(prob, text=f"Model confidence: {prob*100:.1f}%")
        else:
            st.error(f"Prediction failed: {result.get('error')}")

sample_disclaimer()
page_footer()
