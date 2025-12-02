# 🚀 Render Deployment Guide

## Quick Deploy to Render (5 minutes)

### Prerequisites
- GitHub account with this repository pushed
- Render account (https://render.com)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Survival Analysis + Cox Model System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend API

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Connect your GitHub account and select this repository
5. Fill in the form:
   - **Name**: `survival-api`
   - **Environment**: `Docker`
   - **Region**: `us-east` (or your preferred region)
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Dockerfile Path**: `./Dockerfile.backend` (optional, auto-detected)
6. Under **Environment**:
   - Add variable `PORT` = `8000`
   - Add variable `PYTHONUNBUFFERED` = `1`
7. Click **"Create Web Service"**

⏳ Wait 5-10 minutes for deployment. You'll get a URL like:
```
https://survival-api-xxxxx.onrender.com
```

### Step 3: Deploy Frontend UI

1. Click **"New +"** → **"Web Service"** again
2. Select your repository again
3. Fill in the form:
   - **Name**: `survival-ui`
   - **Environment**: `Python 3`
   - **Region**: `us-east`
   - **Branch**: `main`
   - **Root Directory**: `./frontend`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
     ```
4. Under **Environment**, add:
   - `API_URL` = `https://survival-api-xxxxx.onrender.com` (from Step 2)
   - `PYTHONUNBUFFERED` = `1`

5. Click **"Create Web Service"**

⏳ Wait 5-10 minutes. You'll get a URL like:
```
https://survival-ui-xxxxx.onrender.com
```

### Step 4: Test Your Deployment

1. Visit: `https://survival-ui-xxxxx.onrender.com`
2. Test API directly: `https://survival-api-xxxxx.onrender.com/health`
3. API Docs: `https://survival-api-xxxxx.onrender.com/docs`

---

## Alternative: Render.yaml Deployment (One-Click)

**Note**: Render's free tier has limitations. For production use, consider paid plans.

### Using render.yaml (Experimental)

1. Ensure `render.yaml` is in repository root ✓ (already created)
2. Go to https://render.com/dashboard
3. Click **"New +"** → **"Blueprint"**
4. Connect GitHub and select repository
5. Render automatically deploys both services

---

## Environment Variables

### Backend Service
```
PORT=8000
PYTHONUNBUFFERED=1
```

### Frontend Service
```
API_URL=https://survival-api-xxxxx.onrender.com
PYTHONUNBUFFERED=1
```

---

## Troubleshooting

### "Service failed to start"
- Check the **Logs** tab in Render dashboard
- Ensure `Dockerfile.backend` exists in root
- Verify `models/cox_model.pkl` is in repository

### "API connection refused"
- Update `API_URL` environment variable in frontend service
- Wait for backend to fully deploy (check `/health` endpoint)
- Check CORS is enabled (it is by default)

### "Streamlit not finding module"
- Ensure `requirements.txt` includes all dependencies
- Check `buildCommand` in Render service settings
- Rebuild service from Render dashboard

### Memory/Timeout Issues
- Render free tier has 512MB RAM
- Consider upgrading to Starter Plan ($7/month) for more resources
- Or deploy on Google Cloud Run (see README.md)

---

## Cost Estimate

- **Free Tier**: 
  - ❌ Limited to 750 hours/month (~1 service running continuously)
  - ❌ Services spin down after 15 minutes of inactivity
  
- **Starter Plan** ($7/month per service):
  - ✅ Always on
  - ✅ 1GB RAM per service
  - ✅ Free SSL certificate
  - Cost: ~$14/month for both services

---

## Next Steps

After deployment:

1. **Monitor**: Check Render dashboard for logs
2. **Share**: Your app is live! Share the URL
3. **Custom Domain**: Add your domain in Render settings
4. **Backups**: Ensure models are in repository (not generated on deploy)

---

## Advanced: GitHub Actions Integration

For automatic deployments on push:

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Render Deploy
        run: |
          curl -X POST \
            https://api.render.com/deploy/srv-xxxxx \
            -H "Authorization: Bearer ${{ secrets.RENDER_DEPLOY_HOOK }}"
```

Get your deploy hook from Render service settings → Deploy Hook.

---

**Your app is ready to deploy! Choose Render for simplicity or Google Cloud Run for production.**
