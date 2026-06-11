"""Cloud Services — multi-cloud integration status center."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

st.set_page_config(page_title="Cloud Services · Prologis AI", page_icon="☁️", layout="wide", initial_sidebar_state="expanded")

from app.ui_styles import apply_global_styles, hero_card, page_footer
apply_global_styles()

from app.cloud_stubs import AnthropicClient, VertexAIAgent, BedrockClient, SageMakerClient

_anthropic = AnthropicClient()
_vertex    = VertexAIAgent()
_bedrock   = BedrockClient()
_sagemaker = SageMakerClient()

hero_card(
    "Cloud Services",
    "Multi-cloud integration status · Vertex AI ADK · AWS SageMaker · AWS Bedrock · Local fallback mode",
    "☁️",
)

# ── Top status summary grid ───────────────────────────────────────────────────
def _status_kpi(label, value, active):
    color = "#4ade80" if active else "#f59e0b"
    bg    = "rgba(74,222,128,0.08)" if active else "rgba(245,158,11,0.08)"
    bdr   = "rgba(74,222,128,0.25)" if active else "rgba(245,158,11,0.25)"
    return f"""
<div class="fa-kpi-card" style="border-color:{bdr};background:{bg};">
  <div class="fa-kpi-label">{label}</div>
  <div style="font-size:1.05rem;font-weight:800;color:{color};margin-top:4px;">{value}</div>
</div>"""

st.markdown(f"""
<div class="fa-kpi-grid">
  {_status_kpi("Local Mode",     "● Active",         True)}
  {_status_kpi("Vertex AI ADK",  "● Not Configured", False)}
  {_status_kpi("AWS SageMaker",  "● Local Fallback",  False)}
  {_status_kpi("AWS Bedrock",    "● Not Configured", False)}
</div>
""", unsafe_allow_html=True)

# ── Fallback explanation card ─────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0c2340,#1e293b);
  border:1px solid #2d3f55;border-left:4px solid #38bdf8;
  border-radius:12px;padding:1.1rem 1.4rem;margin-bottom:1.5rem;
  box-sizing:border-box;">
  <div style="font-size:0.75rem;font-weight:700;color:#38bdf8;text-transform:uppercase;
              letter-spacing:0.08em;margin-bottom:6px;">Local Fallback Mode Active</div>
  <div style="font-size:0.87rem;color:#94a3b8;line-height:1.6;">
    The application runs fully without cloud credentials using
    <strong style="color:#e2e8f0;">PostgreSQL</strong>,
    <strong style="color:#e2e8f0;">sample SEC metrics</strong>,
    <strong style="color:#e2e8f0;">press release data</strong>, and
    <strong style="color:#e2e8f0;">local scikit-learn ML models</strong>.
    Cloud services can be enabled at any time by adding environment variables to <code>.env</code>
    and restarting Streamlit — no code changes required.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Architecture flow ─────────────────────────────────────────────────────────
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>System Architecture</div>",
            unsafe_allow_html=True)

st.markdown("""
<div class="fa-flow">
  <div class="fa-flow-node">👤 User Question</div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node">🖥 Streamlit App</div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node">🤖 Chatbot Router</div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node" style="border-color:#f59e0b;color:#fcd34d;">
    Vertex AI ADK <span style="color:#475569;">or</span> Local Fallback
  </div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node">🗄 Postgres / SEC / Press Releases</div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node" style="border-color:#f59e0b;color:#fcd34d;">
    SageMaker <span style="color:#475569;">or</span> Local ML
  </div>
  <div class="fa-flow-arrow">→</div>
  <div class="fa-flow-node" style="border-color:#4ade80;color:#4ade80;">✓ Final Answer</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Service cards (2-column grid) ─────────────────────────────────────────────
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.75rem;'>Service Status</div>",
            unsafe_allow_html=True)

_SERVICES = [
    {
        "name":    "GCP Vertex AI ADK",
        "icon":    "🔵",
        "client":  _vertex,
        "purpose": "Advanced chatbot routing and agent orchestration via the Vertex AI Agent Development Kit.",
        "env_vars": [
            ("VERTEX_PROJECT",                "Your GCP project ID"),
            ("VERTEX_LOCATION",               "e.g. us-central1"),
            ("GOOGLE_APPLICATION_CREDENTIALS","Path to service account JSON"),
        ],
        "env_block": "VERTEX_PROJECT=my-project\nVERTEX_LOCATION=us-central1\nGOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json",
        "install":   "pip install google-cloud-aiplatform vertexai",
    },
    {
        "name":    "AWS SageMaker",
        "icon":    "🟠",
        "client":  _sagemaker,
        "purpose": "Hosts the trained Random Forest Regressor and Logistic Regression classifier as live prediction endpoints.",
        "env_vars": [
            ("AWS_ACCESS_KEY_ID",      "IAM access key"),
            ("AWS_SECRET_ACCESS_KEY",  "IAM secret key"),
            ("AWS_REGION",             "e.g. us-east-1"),
            ("SAGEMAKER_RF_ENDPOINT",  "Random Forest endpoint name"),
            ("SAGEMAKER_LR_ENDPOINT",  "Logistic Regression endpoint name"),
        ],
        "env_block": "AWS_ACCESS_KEY_ID=AKIA...\nAWS_SECRET_ACCESS_KEY=...\nAWS_REGION=us-east-1\nSAGEMAKER_RF_ENDPOINT=rf-housing-endpoint\nSAGEMAKER_LR_ENDPOINT=lr-bank-endpoint",
        "install":   "pip install boto3 sagemaker",
    },
    {
        "name":    "AWS Bedrock",
        "icon":    "🟡",
        "client":  _bedrock,
        "purpose": "Multi-cloud LLM summarization fallback using Amazon Titan or Claude via AWS Bedrock.",
        "env_vars": [
            ("AWS_ACCESS_KEY_ID",     "IAM access key"),
            ("AWS_SECRET_ACCESS_KEY", "IAM secret key"),
            ("AWS_REGION",            "e.g. us-east-1"),
            ("BEDROCK_MODEL_ID",      "e.g. amazon.titan-text-express-v1  (optional)"),
        ],
        "env_block": "AWS_ACCESS_KEY_ID=AKIA...\nAWS_SECRET_ACCESS_KEY=...\nAWS_REGION=us-east-1\nBEDROCK_MODEL_ID=amazon.titan-text-express-v1",
        "install":   "pip install boto3",
    },
    {
        "name":    "Anthropic Claude",
        "icon":    "🟣",
        "client":  _anthropic,
        "purpose": "Powers the Chat Assistant with natural language understanding and contextual financial reasoning.",
        "env_vars": [
            ("ANTHROPIC_API_KEY", "Your Anthropic API key (sk-ant-...)"),
        ],
        "env_block": "ANTHROPIC_API_KEY=sk-ant-...",
        "install":   "pip install anthropic",
    },
]

# Render in a 2-column CSS grid
cards_html = ""
for svc in _SERVICES:
    status     = svc["client"].status()
    configured = status.get("configured", False)
    dot_col    = "#4ade80" if configured else "#f59e0b"
    border_col = "rgba(74,222,128,0.3)" if configured else "rgba(245,158,11,0.25)"
    state_text = "● Active" if configured else "● Not configured"
    state_bg   = "rgba(74,222,128,0.1)"  if configured else "rgba(245,158,11,0.1)"

    env_rows = "".join(
        f"<tr><td style='padding:3px 8px 3px 0;font-size:0.72rem;color:#7dd3fc;"
        f"font-family:monospace;white-space:nowrap;'>{k}</td>"
        f"<td style='padding:3px 0;font-size:0.72rem;color:#64748b;'>{desc}</td></tr>"
        for k, desc in svc["env_vars"]
    )

    cards_html += f"""
<div class="fa-service-card" style="border:1px solid {border_col};border-left:3px solid {dot_col};">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;
              margin-bottom:0.65rem;flex-wrap:wrap;gap:0.5rem;">
    <div style="font-size:1rem;font-weight:700;color:#e2e8f0;">{svc['icon']} {svc['name']}</div>
    <span style="background:{state_bg};border:1px solid {border_col};border-radius:99px;
      padding:2px 10px;font-size:0.69rem;font-weight:700;color:{dot_col};white-space:nowrap;">
      {state_text}
    </span>
  </div>
  <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:0.75rem;line-height:1.55;
              overflow-wrap:break-word;">{svc['purpose']}</div>
  <div style="font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;
              letter-spacing:0.08em;margin-bottom:5px;">Required env vars</div>
  <table style="border-collapse:collapse;width:100%;margin-bottom:0.75rem;">{env_rows}</table>
  <div style="font-size:0.69rem;font-weight:700;color:#64748b;text-transform:uppercase;
              letter-spacing:0.08em;margin-bottom:3px;">Install</div>
  <code style="font-size:0.73rem;">{svc['install']}</code>
</div>
"""

st.markdown(f'<div class="fa-cloud-grid">{cards_html}</div>', unsafe_allow_html=True)

# ── How to enable — expandable per service ────────────────────────────────────
st.divider()
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>Configuration Reference</div>",
            unsafe_allow_html=True)

for svc in _SERVICES:
    with st.expander(f"How to enable {svc['name']}"):
        st.markdown(f"**{svc['name']}** — {svc['purpose']}")
        st.markdown("Add to your `.env` file and restart Streamlit:")
        st.code(svc["env_block"], language="bash")
        st.markdown(f"Install dependency: `{svc['install']}`")

st.divider()

# ── SageMaker deployment guide ────────────────────────────────────────────────
st.markdown("<div style='font-size:1rem;font-weight:700;color:#cbd5e1;margin-bottom:0.6rem;'>SageMaker Deployment Guide</div>",
            unsafe_allow_html=True)

with st.expander("Step-by-step: deploy models to SageMaker"):
    st.markdown("""
**Step 1** — Train and save models locally:
```bash
python train_models.py
```

**Step 2** — Package and upload artifacts to S3:
```bash
tar -czf rf_model.tar.gz -C models random_forest_regressor.pkl rf_scaler.pkl rf_feature_names.json
tar -czf lr_model.tar.gz -C models logistic_regression_classifier.pkl lr_scaler.pkl lr_label_encoders.pkl lr_feature_names.json lr_target_encoder.pkl

aws s3 cp rf_model.tar.gz s3://your-bucket/models/rf/model.tar.gz
aws s3 cp lr_model.tar.gz s3://your-bucket/models/lr/model.tar.gz
```

**Step 3** — Deploy via SageMaker Python SDK:
```python
from sagemaker.sklearn import SKLearnModel

rf_model = SKLearnModel(
    model_data="s3://your-bucket/models/rf/model.tar.gz",
    role="arn:aws:iam::ACCOUNT:role/SageMakerRole",
    entry_point="inference_rf.py",
    framework_version="1.2-1",
)
rf_predictor = rf_model.deploy(instance_type="ml.m5.large", initial_instance_count=1)
print("RF endpoint:", rf_predictor.endpoint_name)
```

**Step 4** — Add endpoint names to `.env`:
```
SAGEMAKER_RF_ENDPOINT=rf-housing-endpoint
SAGEMAKER_LR_ENDPOINT=lr-bank-endpoint
```
""")

# ── Demo readiness card ───────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0c2340,#1e293b);
  border:1px solid #2d3f55;border-left:4px solid #4ade80;
  border-radius:12px;padding:1.1rem 1.4rem;margin-top:1.5rem;box-sizing:border-box;">
  <div style="font-size:0.75rem;font-weight:700;color:#4ade80;text-transform:uppercase;
              letter-spacing:0.08em;margin-bottom:6px;">Demo Readiness</div>
  <div style="font-size:0.87rem;color:#94a3b8;line-height:1.6;">
    <strong style="color:#e2e8f0;">Development mode is fully functional locally.</strong>
    All pages — chat, property explorer, SEC filings, press releases, and ML predictions — work
    without any cloud credentials. For the final cloud demonstration, configure
    Vertex AI ADK, SageMaker endpoints, and Bedrock credentials, then record the cloud setup
    workflow as part of the <em>Cloud Configuration Recording</em> deliverable.
  </div>
</div>
""", unsafe_allow_html=True)

page_footer()
