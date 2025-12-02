# 🚀 Quick Start Guide

## 5-Minute Setup (Local Development)

### Step 1: Install Python Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install separately by component
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Step 2: Generate Trained Model

Run the Jupyter notebook to train the model:

```bash
jupyter notebook notebooks/01_Survival_Analysis_Cox_Model.ipynb
```

This will:
- Load the heart.csv dataset
- Perform exploratory analysis
- Train the Cox model
- Export model to `models/` directory

**⏱️ Expected runtime: 2-3 minutes**

### Step 3: Start Backend API

In terminal 1:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend will be available at: http://localhost:8000

### Step 4: Start Frontend

In terminal 2:

```bash
cd frontend
streamlit run app.py
```

✅ Frontend will be available at: http://localhost:8501

### Step 5: Test the API

In terminal 3:

```bash
python test_api.py
```

This runs comprehensive tests on all endpoints.

---

## Docker Setup (Single Command)

### Prerequisites
- Docker and Docker Compose installed

### Launch Everything

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

Services:
- **API**: http://localhost:8000
- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

### Stop Services

```bash
docker-compose down
```

---

## File Structure After Training

After running the notebook, your directory will look like:

```
.
├── heart.csv
├── notebooks/
│   └── 01_Survival_Analysis_Cox_Model.ipynb
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── models/
│   ├── cox_model.pkl              ← Generated
│   ├── preprocessing_artifacts.pkl ← Generated
│   └── model_summary.txt          ← Generated
├── data/
│   ├── train.csv                  ← Generated
│   └── test.csv                   ← Generated
└── ...
```

---

## Troubleshooting

### Issue: Model not found
**Solution**: Run the Jupyter notebook first to generate `models/cox_model.pkl`

### Issue: Port 8000 already in use
**Solution**: 
```bash
# Change port in backend/main.py or use:
lsof -i :8000
kill -9 <PID>
```

### Issue: Streamlit not connecting to API
**Solution**: 
- Check API is running: http://localhost:8000/health
- Update API_URL in Streamlit sidebar
- Check firewall/network settings

### Issue: Docker build fails
**Solution**:
```bash
docker-compose build --no-cache
```

---

## Next Steps

1. **Explore the Notebook**: Review `notebooks/01_Survival_Analysis_Cox_Model.ipynb` for detailed analysis
2. **Test the API**: Use `test_api.py` or Swagger UI at http://localhost:8000/docs
3. **Modify the UI**: Customize `frontend/app.py` for your needs
4. **Deploy**: See README.md for cloud deployment options

---

## Common Tasks

### Train with Different Data
1. Replace `heart.csv` with your dataset
2. Update column mappings in notebook
3. Re-run notebook cells

### Modify API Endpoints
1. Edit `backend/main.py`
2. Restart with `uvicorn main:app --reload`
3. Check new docs at http://localhost:8000/docs

### Customize UI
1. Edit `frontend/app.py`
2. Streamlit auto-reloads on save
3. Add new components in Streamlit sidebar

---

## Performance Tips

- **Notebook training**: ~2-3 minutes
- **API response time**: <500ms per prediction
- **Batch predictions**: 100 patients in ~1 second
- **Model size**: ~2MB (cox_model.pkl + artifacts)

---

## Getting Help

- Check README.md for complete documentation
- Review notebook for methodology
- Use `test_api.py` to verify setup
- Check API docs: http://localhost:8000/docs

---

**You're all set! 🎉**

Start with Step 1 and you'll have a working Survival Analysis API and UI in minutes!
