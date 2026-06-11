# Demo Script — Prologis AI Financial Intelligence Platform

## Business Context
Prologis AI is a financial assistant for Prologis, a real estate investment company.
The platform provides chatbot-based financial analysis, SEC filing insights, press release
intelligence, ML predictions, and cloud-ready integrations — all running locally without
any paid cloud credentials.

---

## Demo Flow

### 1. Open the app
```
streamlit run app/streamlit_app.py
```
Open http://localhost:8501 in your browser.

Point out:
- Dark enterprise UI consistent with a professional financial tool
- Sidebar: Prologis AI brand at top, then navigation
- Home dashboard: KPI cards, SEC filings, press releases

---

### 2. Chat Assistant
Navigate to **Chat Assistant**.

**Ask:** "What was net income in 2024?"
- Expected: Pulls FY2024 financials from PostgreSQL
- Source label: `Source: Local (rule-based) · Intent: financials_summary`

**Ask:** "Show me industrial properties in Chicago"
- Expected: Lists industrial properties in Chicago from the property table
- Source label: `Source: Local (rule-based) · Intent: properties`

**Ask:** "Any recent acquisitions?"
- Expected: Shows acquisition press releases from the mock data
- Source label: `Source: Local (rule-based) · Intent: press_releases`

**Ask about another company (scope guard demo):**
"What is Google's revenue?"
- Expected: "This assistant is configured for Prologis sample data only."

**Ask about unavailable year:**
"Show me 2019 financials"
- Expected: "No data is available for 2019. Available fiscal years: 2023, 2024"

---

### 3. Property Explorer
Navigate to **Property Explorer**.

- Filter by City: Chicago → shows Chicago properties
- Filter by Type: Industrial → shows industrial properties
- Show the KPI row: total properties, avg revenue, avg occupancy
- Show the financial breakdown table

---

### 4. SEC Filings
Navigate to **SEC Filings**.

- Show the 10-K FY2023 expanded with all metrics
- Filter to 10-Q → shows Q1–Q3 2024 quarterly reports
- Show the metric trend chart (select Revenue)

---

### 5. Press Releases
Navigate to **Press Releases**.

- Show all 8 press releases across categories
- Filter by category: Acquisition → shows acquisition releases
- Search keyword: "Chicago" → filters by keyword

---

### 6. ML Predictions
Navigate to **ML Predictions**.

**Housing Value Regression:**
- Show model performance: R² = 0.805, RMSE = 0.506
- Adjust MedInc to 5.0, HouseAge to 20
- Click "Run Housing Value Prediction"
- Expected: Shows predicted median house value ~$250,000–$400,000

**Subscription Classification:**
- Show model performance: Accuracy = 0.818, F1 = 0.509
- Change job to "management", education to "tertiary"
- Click "Run Subscription Prediction"
- Expected: Shows WILL / WILL NOT SUBSCRIBE with confidence %

---

### 7. Cloud Services
Navigate to **Cloud Services**.

Point out:
- Status grid: Local Mode Active, others Not Configured
- Architecture flow diagram: User → Streamlit → Chatbot Router → Local Fallback → Data
- Service cards: all four services show "Not configured" — no crash
- Configuration guides for Vertex AI, SageMaker, Bedrock, Anthropic

**Key message:**
> "The app is fully functional in local development mode. When cloud credentials are
> added to .env and Streamlit is restarted, each service activates automatically — no
> code changes required."

---

### 8. Business Value Summary

| Capability | Status |
|---|---|
| Natural language chatbot | ✅ Rule-based, swap in LLM via .env |
| Property database | ✅ 25 properties, 5 metros, FY2023–2024 |
| SEC filing insights | ✅ 10-K + 3 × 10-Q loaded |
| Press release intelligence | ✅ 8 releases, keyword search |
| ML predictions | ✅ RF Regressor + LR Classifier, local scikit-learn |
| Cloud-ready architecture | ✅ Vertex AI, SageMaker, Bedrock, Anthropic stubs |
| Zero-credential local mode | ✅ Runs fully without API keys |

---

## Local Setup (for evaluators)

```bash
# 1. Clone
git clone https://github.com/ashika2031/financial_assistant.git
cd financial_assistant

# 2. Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Start PostgreSQL
docker run --name financial-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=real_estate_db \
  -p 5432:5432 -d postgres:15

# 4. Configure
cp .env.example .env
# Edit .env if needed (default works with the Docker command above)

# 5. Seed database
python setup_database.py --init

# 6. Train ML models
python train_models.py

# 7. Run
streamlit run app/streamlit_app.py
```

Open http://localhost:8501.
