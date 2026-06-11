# Financial Assistant — Acme Realty Corp

AI-powered financial and property intelligence platform built with Streamlit, PostgreSQL, scikit-learn, and cloud service stubs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (6 pages)                │
│  Home · Chat Assistant · Property Explorer · SEC Filings │
│  Press Releases · ML Predictions · Cloud Services        │
└────────────┬─────────────┬──────────────┬───────────────┘
             │             │              │
     ┌───────▼──────┐ ┌────▼────┐ ┌──────▼──────────┐
     │  PostgreSQL  │ │  JSON   │ │  Local ML Models │
     │  Properties  │ │  Data   │ │  RF + LR (.pkl)  │
     │  Financials  │ │SEC/PRs  │ └──────┬──────────┘
     └──────────────┘ └─────────┘        │ fallback
                                  ┌──────▼──────────┐
                                  │  Cloud Stubs     │
                                  │  SageMaker       │
                                  │  Vertex AI ADK   │
                                  │  AWS Bedrock     │
                                  │  Anthropic Claude│
                                  └─────────────────┘
```

### Data Flow
1. User sends a message → `chatbot.py` detects intent
2. Chatbot fetches data from Postgres / SEC JSON / press release JSON
3. If cloud LLM is configured, data + question are sent to Claude or Vertex AI
4. Otherwise, rule-based templates format the response
5. ML Predictions page loads `.pkl` models locally or calls SageMaker endpoint

---

## Local Setup

### Prerequisites
- Python 3.10+
- Docker (for PostgreSQL)

### 1. Start PostgreSQL

```bash
docker run --name financial-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=real_estate_db \
  -p 5432:5432 -d postgres:16
```

Or if the container already exists:
```bash
docker start financial-postgres
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — DATABASE_URL is already set for local Docker
```

Minimum `.env`:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/real_estate_db
USE_SAMPLE_2024=1
```

### 4. Initialize database and train models

```bash
python setup_database.py --init      # creates tables, seeds 25 properties + financials
python train_models.py               # trains RF regressor + LR classifier, saves .pkl files
```

### 5. Run the app

```bash
streamlit run app/streamlit_app.py
```

Open **http://localhost:8501**

---

## Pages

| Page | Description |
|------|-------------|
| **Home** | KPI dashboard, latest SEC filing, recent press releases |
| **Chat Assistant** | Natural language Q&A across all data sources |
| **Property Explorer** | Filter and browse properties with financial breakdowns |
| **SEC Filings** | Annual (10-K) and quarterly (10-Q) report viewer |
| **Press Releases** | Company announcements with category and keyword filters |
| **ML Predictions** | Housing value regression + subscription classification |
| **Cloud Services** | Status and configuration guide for all cloud integrations |

---

## Machine Learning Models

### Regression — Random Forest on California Housing

- **Dataset**: California Housing (scikit-learn built-in)
- **Model**: `RandomForestRegressor(n_estimators=100)`
- **Features**: MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude
- **Metrics**: RMSE ≈ 0.51, MAE ≈ 0.33, R² ≈ 0.80
- **Artifact**: `models/random_forest_regressor.pkl` + `models/rf_scaler.pkl`

### Classification — Logistic Regression on Bank Marketing

- **Dataset**: Bank Marketing (UCI ML Repository, id=222)
- **Model**: `LogisticRegression(max_iter=1000, class_weight='balanced')`
- **Target**: Predict subscription (yes/no)
- **Preprocessing**: LabelEncoder for categoricals, StandardScaler for numerics
- **Metrics**: Accuracy ≈ 0.82, F1 ≈ 0.51, Recall ≈ 0.78
- **Artifact**: `models/logistic_regression_classifier.pkl` + `models/lr_scaler.pkl` + `models/lr_label_encoders.pkl`

---

## Chatbot Query Routing

The chatbot in `app/chatbot.py` detects intent from keywords:

| User says... | Intent | Data source |
|---|---|---|
| "net income", "revenue", "earnings" | `financials_summary` | PostgreSQL |
| "properties", "office", metro names | `properties` | PostgreSQL |
| "10-K", "10-Q", "annual report" | `sec_filing` | SEC JSON |
| "acquisition", "press release", "expansion" | `press_releases` | Press releases JSON |
| "summary", "overview", "portfolio" | `portfolio_summary` | PostgreSQL |

If `ANTHROPIC_API_KEY` is set, Claude handles the response using fetched data as context.
If Vertex AI is configured, Gemini handles it. Otherwise, templates format the data locally.

---

## Cloud Configuration

All cloud services are optional. The app runs fully locally without any API keys.

### Anthropic Claude (chatbot)
```
ANTHROPIC_API_KEY=sk-ant-...
```

### GCP Vertex AI ADK (chatbot alternative)
```
VERTEX_PROJECT=your-gcp-project-id
VERTEX_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```
Install: `pip install google-cloud-aiplatform vertexai`

### AWS SageMaker (ML endpoints)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
SAGEMAKER_RF_ENDPOINT=rf-housing-endpoint
SAGEMAKER_LR_ENDPOINT=lr-bank-endpoint
```

**SageMaker deployment steps:**
1. Train models: `python train_models.py`
2. Package artifacts as `model.tar.gz` and upload to S3
3. Deploy via SageMaker Python SDK (SKLearnModel)
4. Set endpoint names in `.env`

### AWS Bedrock (summarization)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1  # optional, this is the default
```

---

## Project Structure

```
financial-assistant-project/
├── app/
│   ├── streamlit_app.py      # Main entry point (home dashboard)
│   ├── admin.py              # Admin / Debug page
│   ├── chatbot.py            # Intent detection + response routing
│   ├── cloud_stubs.py        # Cloud service wrappers (Anthropic/Vertex/SageMaker/Bedrock)
│   ├── config.py             # .env loader
│   ├── db.py                 # DB health check + reseed helpers
│   ├── init_db.py            # Table creation + 25-property seed
│   ├── ml_inference.py       # Load .pkl models + run predictions
│   ├── press_releases.py     # Press release loader/search
│   ├── queries.py            # Property + financial SQL helpers
│   ├── sec_edgar.py          # SEC filing data loader
│   └── pages/
│       ├── 1_Chat_Assistant.py
│       ├── 2_Property_Explorer.py
│       ├── 3_SEC_Filings.py
│       ├── 4_Press_Releases.py
│       ├── 5_ML_Predictions.py
│       └── 6_Cloud_Services.py
├── data/
│   ├── press_releases.json   # 8 sample press releases
│   └── sec_filings.json      # 4 sample filings (1x 10-K, 3x 10-Q)
├── models/
│   ├── random_forest_regressor.pkl
│   ├── rf_scaler.pkl
│   ├── rf_feature_names.json
│   ├── logistic_regression_classifier.pkl
│   ├── lr_scaler.pkl
│   ├── lr_label_encoders.pkl
│   ├── lr_feature_names.json
│   ├── lr_target_encoder.pkl
│   └── model_metrics.json
├── scripts/
│   ├── reseed_2024.py
│   └── reseed_2024.sh
├── setup_database.py         # CLI: --init / --health / --reseed
├── train_models.py           # Train and save both ML models
├── requirements.txt
└── .env
```
