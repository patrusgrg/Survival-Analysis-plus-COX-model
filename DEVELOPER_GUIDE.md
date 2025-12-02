# 🛠️ Developer Guide

## Extending the Project

This guide helps developers customize and extend the Survival Analysis project.

---

## 🔧 Backend Modifications

### Adding New API Endpoints

**File**: `backend/main.py`

**Example - Add a custom risk calculator endpoint**:

```python
@app.post("/calculate-risk-score")
async def calculate_risk_score(patient: PatientInput):
    """Custom risk calculation based on domain expertise"""
    
    if cox_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        patient_df = pd.DataFrame([patient.dict()])
        feature_names = preprocessing.get('feature_names', [])
        patient_df = patient_df[feature_names]
        
        # Get hazard ratio
        hazard = cox_model.predict_partial_hazard(patient_df).values[0]
        
        # Custom scoring logic
        risk_score = (hazard - 0.5) * 100  # Scale to 0-200
        
        return {
            "risk_score": float(risk_score),
            "interpretation": "High" if risk_score > 100 else "Medium" if risk_score > 50 else "Low"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
```

### Adding Database Support

**Add to `backend/requirements.txt`**:
```
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # For PostgreSQL
```

**Example - Save predictions to database**:

```python
from sqlalchemy import create_engine
from datetime import datetime

DATABASE_URL = "postgresql://user:password@localhost/survival_db"
engine = create_engine(DATABASE_URL)

@app.post("/predict-and-save")
async def predict_and_save(patient: PatientInput):
    # Get prediction
    prediction = await predict(patient)
    
    # Save to database
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO predictions (patient_data, prediction, timestamp) VALUES (%s, %s, %s)",
            (json.dumps(patient.dict()), json.dumps(prediction), datetime.now())
        )
        conn.commit()
    
    return prediction
```

### Adding Authentication

**Add to `backend/requirements.txt`**:
```
python-jose==3.3.0
passlib==1.7.4
```

**Example - Token-based authentication**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    return username

@app.post("/predict")
async def predict(patient: PatientInput, current_user: str = Depends(get_current_user)):
    # ... existing prediction logic
```

---

## 🎨 Frontend Customizations

### Modifying the Input Form

**File**: `frontend/app.py`

**Add new patient input parameter**:

```python
# Add in the input form section
with st.form("patient_form"):
    col_a, col_b = st.columns(2)
    
    with col_a:
        # ... existing inputs
        new_parameter = st.slider(
            "New Parameter",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            help="Helpful description here"
        )
    
    patient_data["new_parameter"] = new_parameter
```

### Adding Custom Visualizations

**Example - Risk timeline**:

```python
import plotly.graph_objects as go

def plot_risk_timeline(prediction):
    """Interactive timeline of risk over time"""
    
    survival_probs = prediction.get("survival_probabilities", {})
    
    ages = sorted([int(k) for k in survival_probs.keys()])
    risks = [1 - survival_probs[str(age)] for age in ages]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=ages, y=risks,
        mode='lines+markers',
        name='Risk Over Time',
        line=dict(color='#d62828', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Risk Progression Over Time",
        xaxis_title="Age (years)",
        yaxis_title="Risk Score (0-1)",
        hovermode='x unified'
    )
    
    return fig

# In main prediction display:
if submit_button:
    fig = plot_risk_timeline(prediction)
    st.plotly_chart(fig, use_container_width=True)
```

### Multi-page Streamlit App

**Create `frontend/pages/analytics.py`**:

```python
import streamlit as st

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊 Analytics Dashboard")

# Add your analytics content here
# This will appear as a separate page in the Streamlit app
```

### Dark Mode Support

```python
st.markdown("""
<style>
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #0e1117;
        }
        .metric-box {
            background-color: #161b22;
            border: 1px solid #30363d;
        }
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📊 Model Improvements

### Retraining the Cox Model

**Script**: `retrain_model.py`

```python
import pandas as pd
from lifelines import CoxPHFitter
import joblib

# Load new data
df = pd.read_csv('new_heart_data.csv')

# Prepare features
cox_features = [...]  # Your feature list
train_df = df[cox_features + ['time', 'event']]

# Retrain model
cph = CoxPHFitter()
cph.fit(train_df, duration_col='time', event_col='event')

# Evaluate
print(f"C-Index: {cph.concordance_index_}")

# Save new model
joblib.dump(cph, 'models/cox_model_v2.pkl')
print("✅ Model retrained and saved!")
```

### Feature Engineering

**Add new features to `retrain_model.py`**:

```python
# Create polynomial features
df['age_squared'] = df['time'] ** 2
df['bp_cholesterol_interaction'] = df['resting_bp'] * df['cholesterol']

# Log transforms
df['log_cholesterol'] = np.log1p(df['cholesterol'])
df['log_max_hr'] = np.log1p(df['max_hr'])

# Binning
df['age_groups'] = pd.cut(df['time'], bins=[0, 50, 60, 70, 100])

# Include in model training
cox_features.extend(['age_squared', 'bp_cholesterol_interaction', 'log_cholesterol'])
```

### Ensemble Approaches

**Create `backend/ensemble_model.py`**:

```python
from lifelines import CoxPHFitter, WeibullAFTFitter
import numpy as np

class EnsembleModel:
    def __init__(self):
        self.cox = CoxPHFitter()
        self.weibull = WeibullAFTFitter()
    
    def fit(self, df, duration_col, event_col):
        self.cox.fit(df, duration_col, event_col)
        self.weibull.fit(df, duration_col, event_col)
    
    def predict(self, X):
        cox_pred = self.cox.predict_partial_hazard(X).values
        weibull_pred = self.weibull.predict_median(X).values
        
        # Average predictions
        return np.mean([cox_pred, weibull_pred], axis=0)
```

---

## 🐳 Advanced Docker Configuration

### Multi-stage Build for Optimized Image

**Create `Dockerfile.optimized`**:

```dockerfile
# Stage 1: Build
FROM python:3.11 as builder

WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY backend/ .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
```

### Kubernetes Deployment

**Create `k8s/deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: survival-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: survival-api
  template:
    metadata:
      labels:
        app: survival-api
    spec:
      containers:
      - name: api
        image: gcr.io/PROJECT_ID/survival-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

---

## 📈 Monitoring & Observability

### Add Prometheus Metrics

**Add to `backend/requirements.txt`**:
```
prometheus-client==0.19.0
```

**Update `backend/main.py`**:

```python
from prometheus_client import Counter, Histogram, generate_latest

predictions_total = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.post("/predict")
async def predict(patient: PatientInput):
    with prediction_latency.time():
        # ... prediction logic
        predictions_total.inc()
    return result

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

### Logging Configuration

**Create `backend/logging_config.py`**:

```python
import logging
import logging.handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler('app.log', maxBytes=10485760, backupCount=10)
    ]
)

logger = logging.getLogger(__name__)
```

---

## 🧪 Testing & Quality Assurance

### Unit Tests

**Create `tests/test_backend.py`**:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_single_prediction():
    patient_data = {
        "time": 55, "sex": 0, "chest_pain_type": 0,
        "resting_bp": 140, "cholesterol": 200, "fasting_bs": 0,
        "resting_ecg": 0, "max_hr": 140, "exercise_angina": 0,
        "oldpeak": 1.0, "st_slope": 1
    }
    
    response = client.post("/predict", json=patient_data)
    assert response.status_code == 200
    assert "hazard_ratio" in response.json()
    assert "risk_score" in response.json()

def test_invalid_input():
    invalid_data = {"time": -10, "sex": 999}
    response = client.post("/predict", json=invalid_data)
    assert response.status_code != 200
```

**Run tests**:
```bash
pytest tests/
```

---

## 🚀 Performance Optimization

### Caching Predictions

**Update `backend/main.py`**:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_predict(patient_tuple):
    patient_dict = dict(patient_tuple)
    return cox_model.predict_partial_hazard(pd.DataFrame([patient_dict])).values[0]

@app.post("/predict-cached")
async def predict_cached(patient: PatientInput):
    patient_tuple = tuple(patient.dict().items())
    return cached_predict(patient_tuple)
```

### Batch Processing Optimization

```python
@app.post("/predict_batch_optimized")
async def predict_batch_optimized(patients: List[PatientInput]):
    patient_df = pd.DataFrame([p.dict() for p in patients])
    feature_names = preprocessing.get('feature_names', [])
    patient_df = patient_df[feature_names]
    
    # Vectorized prediction
    hazards = cox_model.predict_partial_hazard(patient_df).values
    
    return [{"hazard": float(h)} for h in hazards]
```

---

## 📚 Additional Resources

- **Lifelines Documentation**: https://lifelines.readthedocs.io/
- **FastAPI Guide**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

## 🎯 Common Customization Patterns

### Change Model Input/Output
1. Update Pydantic schema in `backend/main.py`
2. Retrain notebook with new features
3. Update API request/response handling

### Add New Data Source
1. Create data loader in notebook
2. Update preprocessing pipeline
3. Retrain model with new data

### Deploy to New Platform
1. Containerize with Docker
2. Update environment variables
3. Configure networking and secrets

---

**Happy Developing! 🎉**

For questions or issues, refer to the main README.md or PROJECT_SUMMARY.md
