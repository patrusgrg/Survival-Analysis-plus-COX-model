"""
FastAPI Backend for Survival Analysis Predictions
Serves Cox Proportional Hazards model predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Survival Analysis API",
    description="Cox Proportional Hazards Model API for Heart Disease Survival Prediction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and artifacts at startup
try:
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'cox_model.pkl')
    ARTIFACTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'preprocessing_artifacts.pkl')
    
    cox_model = joblib.load(MODEL_PATH)
    preprocessing = joblib.load(ARTIFACTS_PATH)
    
    print("✅ Model and artifacts loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    cox_model = None
    preprocessing = None

# Pydantic Models
class PatientInput(BaseModel):
    """Input schema for patient data"""
    time: float  # Age in years
    sex: int  # 0 or 1 (M or F)
    chest_pain_type: int
    resting_bp: float
    cholesterol: float
    fasting_bs: int
    resting_ecg: int
    max_hr: float
    exercise_angina: int
    oldpeak: float
    st_slope: int
    
    class Config:
        schema_extra = {
            "example": {
                "time": 55,
                "sex": 0,
                "chest_pain_type": 0,
                "resting_bp": 140,
                "cholesterol": 200,
                "fasting_bs": 0,
                "resting_ecg": 0,
                "max_hr": 140,
                "exercise_angina": 0,
                "oldpeak": 1.0,
                "st_slope": 1
            }
        }

class PredictionResponse(BaseModel):
    """Output schema for predictions"""
    hazard_ratio: float
    risk_score: str
    median_survival_age: Optional[float]
    survival_probabilities: Dict[int, float]
    timestamp: str

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    timestamp: str

# API Endpoints
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy" if cox_model is not None else "model not loaded",
        model_loaded=cox_model is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(patient: PatientInput):
    """
    Predict survival for a patient using Cox model
    
    Returns:
    - hazard_ratio: Individual hazard ratio (risk score)
    - risk_score: Risk category (Low/Medium/High)
    - median_survival_age: Predicted median survival age
    - survival_probabilities: Survival at key timepoints
    """
    
    if cox_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Convert input to DataFrame
        patient_df = pd.DataFrame([patient.dict()])
        
        # Get feature names
        feature_names = preprocessing.get('feature_names', [])
        patient_df = patient_df[feature_names]
        
        # Calculate hazard ratio (partial hazard)
        partial_hazard = cox_model.predict_partial_hazard(patient_df).values[0]
        
        # Determine risk score
        if partial_hazard < 0.5:
            risk_score = "Low Risk"
        elif partial_hazard < 1.5:
            risk_score = "Medium Risk"
        else:
            risk_score = "High Risk"
        
        # Predict survival function
        survival_func = cox_model.predict_survival_function(patient_df)
        
        # Calculate survival probabilities at key ages
        survival_probs = {}
        current_age = int(patient.time)
        for future_age in [current_age + 5, current_age + 10, current_age + 15, current_age + 20]:
            if future_age <= survival_func.index.max():
                idx = survival_func.index.get_indexer([future_age], method='nearest')[0]
                survival_probs[future_age] = float(survival_func.iloc[idx].values[0])
        
        # Find median survival age
        below_50 = survival_func[survival_func.values.flatten() < 0.5]
        median_survival = float(below_50.index[0]) if len(below_50) > 0 else float(survival_func.index[-1])
        
        return PredictionResponse(
            hazard_ratio=float(partial_hazard),
            risk_score=risk_score,
            median_survival_age=median_survival,
            survival_probabilities=survival_probs,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/predict_batch", response_model=List[Dict])
async def predict_batch(patients: List[PatientInput]):
    """Batch prediction endpoint"""
    
    if cox_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        predictions = []
        
        for patient in patients:
            # Use the predict endpoint logic
            patient_df = pd.DataFrame([patient.dict()])
            feature_names = preprocessing.get('feature_names', [])
            patient_df = patient_df[feature_names]
            
            partial_hazard = cox_model.predict_partial_hazard(patient_df).values[0]
            
            if partial_hazard < 0.5:
                risk_score = "Low Risk"
            elif partial_hazard < 1.5:
                risk_score = "Medium Risk"
            else:
                risk_score = "High Risk"
            
            predictions.append({
                "patient_age": patient.time,
                "hazard_ratio": float(partial_hazard),
                "risk_score": risk_score
            })
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")

@app.get("/model-info")
async def model_info():
    """Get model information"""
    if cox_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    return {
        "model_type": "Cox Proportional Hazards",
        "concordance_index": float(cox_model.concordance_index_),
        "number_of_features": len(preprocessing.get('feature_names', [])),
        "features": preprocessing.get('feature_names', []),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
