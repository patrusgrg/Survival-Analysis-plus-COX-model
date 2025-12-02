# 🏥 Survival Analysis + Cox Proportional Hazards Model

A complete end-to-end machine learning pipeline for survival analysis using the Heart Failure dataset, featuring a trained Cox Proportional Hazards model deployed as a FastAPI backend with an interactive Streamlit frontend.

## 📋 Project Overview

This project implements a comprehensive survival analysis workflow:

1. **Data Analysis**: Exploratory data analysis on 918 heart disease patients
2. **Kaplan-Meier Analysis**: Overall and stratified survival curves
3. **Cox Regression**: Hazard ratio estimation and risk prediction
4. **API Backend**: FastAPI service for predictions
5. **Interactive UI**: Streamlit frontend for user-friendly predictions
6. **Deployment**: Docker containerization and cloud deployment options

## 🎯 Key Features

### Phase 1: Data Understanding & Preparation
- ✅ Load and inspect the heart.csv dataset (918 samples, 11 features)
- ✅ Handle missing values and outliers
- ✅ Encode categorical variables
- ✅ Standardize numerical features
- ✅ 80/20 train/test split

### Phase 2: Survival Analysis
- ✅ Kaplan-Meier survival curves (overall and stratified)
- ✅ Stratification by: Sex, Chest Pain Type, Age Groups
- ✅ Log-rank statistical testing for group differences
- ✅ Median survival estimates

### Phase 3: Cox Model
- ✅ Fit Cox Proportional Hazards model
- ✅ Hazard ratios with 95% confidence intervals
- ✅ Statistical significance testing (p < 0.05)
- ✅ Proportional hazards assumption validation
- ✅ Model concordance (C-Index ≈ 0.85)

### Phase 4: Model Export
- ✅ Trained model saved as joblib pickle
- ✅ Preprocessing artifacts preserved
- ✅ Feature names and mappings stored

### Phase 5: FastAPI Backend
- ✅ REST API endpoints for predictions
- ✅ Batch prediction capability
- ✅ Model information endpoint
- ✅ CORS enabled for frontend integration
- ✅ Health check endpoint

### Phase 6: Streamlit Frontend
- ✅ Interactive patient data input form
- ✅ Real-time risk predictions
- ✅ Risk visualization (Low/Medium/High)
- ✅ Survival probability curves
- ✅ Patient characteristic visualization

### Phase 7: Containerization
- ✅ Docker images for backend and frontend
- ✅ Docker Compose for orchestration
- ✅ Health checks and automatic restart

## 📊 Dataset Information

**Heart Failure Dataset (Kaggle)**

```
Shape: (918, 12)
Event Rate: 55.4% (heart disease positive)
Features:
├── Age: Patient age in years
├── Sex: Male (0) / Female (1)
├── ChestPainType: 4 categories (Typical, Atypical, Non-anginal, Asymptomatic)
├── RestingBP: Resting blood pressure (mmHg)
├── Cholesterol: Serum cholesterol (mg/dL)
├── FastingBS: Fasting blood sugar > 120 mg/dL (0/1)
├── RestingECG: Resting electrocardiogram (3 categories)
├── MaxHR: Maximum heart rate achieved
├── ExerciseAngina: Exercise-induced angina (0/1)
├── Oldpeak: ST depression induced by exercise
├── ST_Slope: Slope of ST segment (3 categories)
└── HeartDisease: Target (0 = No disease, 1 = Disease)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- Git

### Local Development Setup

#### 1. Clone or navigate to project

```bash
cd Survival-Analysis-plus-COX-model
```

#### 2. Install dependencies

**Backend:**
```bash
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
pip install -r frontend/requirements.txt
```

#### 3. Run the notebook (Phase 1-4)

```bash
jupyter notebook notebooks/01_Survival_Analysis_Cox_Model.ipynb
```

This will:
- Load and preprocess the dataset
- Generate Kaplan-Meier curves
- Train the Cox model
- Save trained model to `models/` directory

#### 4. Start FastAPI backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

**API Documentation:**
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 5. Start Streamlit frontend (in new terminal)

```bash
cd frontend
streamlit run app.py
```

Frontend will be available at: `http://localhost:8501`

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
Survival-Analysis-plus-COX-model/
├── heart.csv                          # Raw dataset
├── notebooks/
│   └── 01_Survival_Analysis_Cox_Model.ipynb    # Complete analysis notebook
├── backend/
│   ├── main.py                       # FastAPI application
│   ├── requirements.txt              # Backend dependencies
│   └── Dockerfile                    # Backend container config
├── frontend/
│   ├── app.py                        # Streamlit application
│   ├── requirements.txt              # Frontend dependencies
│   └── Dockerfile                    # Frontend container config
├── models/
│   ├── cox_model.pkl                 # Trained Cox model
│   ├── preprocessing_artifacts.pkl   # Preprocessing metadata
│   └── model_summary.txt             # Model statistics
├── data/
│   ├── train.csv                     # Training set (80%)
│   └── test.csv                      # Test set (20%)
├── docker-compose.yml                # Docker Compose configuration
├── Dockerfile.backend                # Backend Dockerfile
├── README.md                         # This file
└── requirements.txt                  # Root dependencies
```

## 🔌 API Endpoints

### 1. Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### 2. Single Prediction
```bash
POST /predict

{
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
```

Response:
```json
{
  "hazard_ratio": 0.845,
  "risk_score": "Low Risk",
  "median_survival_age": 75.2,
  "survival_probabilities": {
    "60": 0.92,
    "65": 0.87,
    "70": 0.79,
    "75": 0.68
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### 3. Batch Prediction
```bash
POST /predict_batch

[
  {"time": 50, "sex": 0, ...},
  {"time": 60, "sex": 1, ...}
]
```

### 4. Model Information
```bash
GET /model-info
```

Response:
```json
{
  "model_type": "Cox Proportional Hazards",
  "concordance_index": 0.847,
  "number_of_features": 11,
  "features": ["time", "sex", "chest_pain_type", ...],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## 📈 Key Results

### Cox Model Performance
- **Concordance Index**: 0.847 (excellent discrimination)
- **Training Set Size**: 734 patients
- **Test Set Size**: 184 patients
- **Features**: 11 clinical variables

### Significant Predictors (p < 0.05)
- **Max Heart Rate**: HR = 0.98 (protective: higher HR = lower risk)
- **Age**: HR = 1.01 (risk increases with age)
- **Chest Pain Type**: Varies by category
- **Exercise-Induced Angina**: HR ≈ 1.5 (increased risk)

### Survival Statistics
- **Median Survival Age**: ~75 years (overall population)
- **1-Year Survival**: 95%+
- **5-Year Survival**: ~85%
- **10-Year Survival**: ~60%

## 🎯 Streamlit Frontend Features

### Input Form
- 11 clinical parameters
- Real-time validation
- Helpful tooltips and descriptions

### Predictions Display
- **Risk Category**: Low/Medium/High with color coding
- **Hazard Ratio**: Individual risk score
- **Median Survival**: Predicted age
- **Survival Probabilities**: At 5, 10, 15, 20 years ahead

### Visualizations
- **Risk Gauge**: Needle gauge showing risk level
- **Patient Radar Chart**: Normalized patient characteristics
- **Survival Curve**: Predicted survival trajectory

## 🌐 Deployment Options

### Option 1: Render (Simplest) ⭐ RECOMMENDED

**See detailed guide**: [`RENDER_DEPLOY.md`](RENDER_DEPLOY.md)

Quick steps:
1. Push repository to GitHub
2. Go to https://render.com
3. Create Web Service → Connect GitHub → Select Docker
4. Set `PORT=8000`
5. Deploy! (5-10 minutes)

**Includes**:
- `render.yaml` for one-click deployment
- Step-by-step instructions
- Troubleshooting guide
- Cost estimates

### Option 2: Google Cloud Run (Production)

1. **Build Docker image**
```bash
docker build -f Dockerfile.backend -t gcr.io/PROJECT_ID/survival-api:latest .
docker push gcr.io/PROJECT_ID/survival-api:latest
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy survival-api \
  --image gcr.io/PROJECT_ID/survival-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Deploy Frontend on Streamlit Cloud**
   - Push frontend to GitHub
   - Go to https://streamlit.io/cloud
   - Deploy from repository
   - Set `API_URL` secret to your Cloud Run endpoint

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'

# Model info
curl http://localhost:8000/model-info
```

### Test Frontend

1. Open http://localhost:8501
2. Fill in patient data form
3. Click "Predict Survival Risk"
4. Review predictions and visualizations

## 📚 Key References

### Libraries Used
- **lifelines**: Survival analysis and Cox models
- **scikit-learn**: Preprocessing and model utilities
- **pandas/numpy**: Data manipulation
- **matplotlib/seaborn**: Visualizations
- **fastapi**: REST API framework
- **streamlit**: Interactive UI framework

### Theory
- Kaplan-Meier Estimator: Non-parametric survival function
- Cox Proportional Hazards: Semi-parametric regression for censored data
- Log-Rank Test: Statistical test for survival differences
- Schoenfeld Residuals: Proportional hazards assumption validation

## ⚠️ Disclaimer

**This tool is for educational and informational purposes only.**

- Not a substitute for professional medical advice
- Results should be interpreted alongside clinical judgment
- Consult healthcare providers for medical decisions
- Model trained on specific dataset - may not generalize to all populations

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Check existing documentation
- Review notebook for detailed analysis

## 🎓 Learning Outcomes

By exploring this project, you'll learn:
- ✅ Survival analysis fundamentals
- ✅ Kaplan-Meier estimation
- ✅ Cox proportional hazards modeling
- ✅ Statistical hypothesis testing
- ✅ REST API design with FastAPI
- ✅ Interactive UI with Streamlit
- ✅ Docker containerization
- ✅ Cloud deployment strategies
- ✅ End-to-end ML pipeline

## 🎉 Acknowledgments

- Dataset: Kaggle Heart Failure Dataset
- Methods: lifelines documentation
- Inspiration: Applied survival analysis research

---

**Last Updated**: January 2024  
**Status**: Complete & Production-Ready ✅
