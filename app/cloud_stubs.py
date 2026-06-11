"""Cloud service stubs.

Each class checks for the relevant env var / credentials.
If not configured it returns graceful "not configured" responses
so the app runs fully locally without any cloud keys.

To activate:
  Vertex AI ADK  → set GOOGLE_APPLICATION_CREDENTIALS + VERTEX_PROJECT + VERTEX_LOCATION
  SageMaker      → set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY + AWS_REGION
                   and SAGEMAKER_RF_ENDPOINT + SAGEMAKER_LR_ENDPOINT
  Bedrock        → set AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY + AWS_REGION
  Anthropic      → set ANTHROPIC_API_KEY
"""
import os
from typing import Any, Dict, Optional


# ── helpers ────────────────────────────────────────────────────────────────────

def _env(key: str) -> Optional[str]:
    return os.environ.get(key) or None


# ── Vertex AI ADK stub ─────────────────────────────────────────────────────────

class VertexAIAgent:
    """Wraps Vertex AI ADK agent. Falls back to local rule-based chatbot when not configured."""

    def __init__(self):
        self.project   = _env("VERTEX_PROJECT")
        self.location  = _env("VERTEX_LOCATION") or "us-central1"
        self.creds     = _env("GOOGLE_APPLICATION_CREDENTIALS")
        self.configured = bool(self.project and self.creds)

    def status(self) -> Dict:
        return {
            "configured": self.configured,
            "project": self.project or "not set",
            "location": self.location,
            "note": "Set VERTEX_PROJECT and GOOGLE_APPLICATION_CREDENTIALS to enable.",
        }

    def chat(self, message: str, context: Dict = None) -> str:
        if not self.configured:
            return None  # caller falls back to local chatbot
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            vertexai.init(project=self.project, location=self.location)
            model = GenerativeModel("gemini-pro")
            resp = model.generate_content(message)
            return resp.text
        except Exception as e:
            return f"[Vertex AI error: {e}]"


# ── AWS Bedrock stub ───────────────────────────────────────────────────────────

class BedrockClient:
    """Wraps AWS Bedrock for LLM summarization. Falls back to simple local summary."""

    def __init__(self):
        self.access_key = _env("AWS_ACCESS_KEY_ID")
        self.secret_key = _env("AWS_SECRET_ACCESS_KEY")
        self.region     = _env("AWS_REGION") or "us-east-1"
        self.model_id   = _env("BEDROCK_MODEL_ID") or "amazon.titan-text-express-v1"
        self.configured = bool(self.access_key and self.secret_key)

    def status(self) -> Dict:
        return {
            "configured": self.configured,
            "region": self.region,
            "model_id": self.model_id,
            "note": "Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION to enable.",
        }

    def summarize(self, text: str) -> str:
        if not self.configured:
            return None  # caller uses local fallback
        try:
            import boto3, json
            client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            body = json.dumps({"inputText": f"Summarize this in 2 sentences:\n{text}"})
            resp = client.invoke_model(modelId=self.model_id, body=body)
            result = json.loads(resp["body"].read())
            return result.get("results", [{}])[0].get("outputText", "")
        except Exception as e:
            return f"[Bedrock error: {e}]"


# ── SageMaker stub ─────────────────────────────────────────────────────────────

class SageMakerClient:
    """Invokes SageMaker hosted endpoints for RF regression and LR classification."""

    def __init__(self):
        self.access_key  = _env("AWS_ACCESS_KEY_ID")
        self.secret_key  = _env("AWS_SECRET_ACCESS_KEY")
        self.region      = _env("AWS_REGION") or "us-east-1"
        self.rf_endpoint = _env("SAGEMAKER_RF_ENDPOINT")
        self.lr_endpoint = _env("SAGEMAKER_LR_ENDPOINT")
        self.configured  = bool(self.access_key and self.secret_key and self.rf_endpoint and self.lr_endpoint)

    def status(self) -> Dict:
        return {
            "configured": self.configured,
            "rf_endpoint": self.rf_endpoint or "not set",
            "lr_endpoint": self.lr_endpoint or "not set",
            "region": self.region,
            "note": "Set AWS credentials + SAGEMAKER_RF_ENDPOINT + SAGEMAKER_LR_ENDPOINT to enable.",
        }

    def predict_regression(self, features: list) -> Optional[float]:
        if not self.configured:
            return None
        try:
            import boto3, json
            client = boto3.client(
                "sagemaker-runtime",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            resp = client.invoke_endpoint(
                EndpointName=self.rf_endpoint,
                ContentType="application/json",
                Body=json.dumps({"instances": [features]}),
            )
            return float(json.loads(resp["Body"].read())["predictions"][0])
        except Exception as e:
            return None

    def predict_classification(self, features: list) -> Optional[Dict]:
        if not self.configured:
            return None
        try:
            import boto3, json
            client = boto3.client(
                "sagemaker-runtime",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            resp = client.invoke_endpoint(
                EndpointName=self.lr_endpoint,
                ContentType="application/json",
                Body=json.dumps({"instances": [features]}),
            )
            result = json.loads(resp["Body"].read())
            return {"prediction": result["predictions"][0], "probability": result.get("probabilities", [[0.5]])[0]}
        except Exception as e:
            return None


# ── Anthropic stub ─────────────────────────────────────────────────────────────

class AnthropicClient:
    """Claude API client. Falls back gracefully when key is not set."""

    def __init__(self):
        self.api_key    = _env("ANTHROPIC_API_KEY")
        self.configured = bool(self.api_key)
        self.model      = "claude-sonnet-4-6"

    def status(self) -> Dict:
        return {
            "configured": self.configured,
            "model": self.model,
            "note": "Set ANTHROPIC_API_KEY to enable Claude-powered responses.",
        }

    def chat(self, system: str, user: str) -> Optional[str]:
        if not self.configured:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            msg = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return msg.content[0].text
        except Exception as e:
            return f"[Claude API error: {e}]"
