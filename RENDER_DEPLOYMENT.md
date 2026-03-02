# 🚀 Deploy Atlas AI to Render

## Why Render > Vercel for This Project?

| Feature | Render | Vercel |
|---------|--------|--------|
| **Python Backend** | ✅ Full support | ❌ Edge functions only |
| **Long-running processes** | ✅ FastAPI, Streamlit | ❌ 10s timeout |
| **File uploads** | ✅ Native support | ⚠️ Limited |
| **Background workers** | ✅ Yes | ❌ No |
| **Free tier** | ✅ 750 hours/month | ✅ Yes |
| **Best for** | Full-stack Python | Frontend/Next.js |

**Verdict: Use Render** ✅

---

## 📋 Step-by-Step Deployment

### 1️⃣ Prerequisites
- ✅ GitHub repo: https://github.com/Surelinks/ATLAS.git (DONE!)
- ✅ Groq API key: Get free at https://console.groq.com
- ✅ Render account: Sign up at https://render.com

### 2️⃣ Deploy Backend (FastAPI)

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Click **"Connect account"** → Select GitHub
   - Find and select **"Surelinks/ATLAS"** repository

3. **Configure Backend Service**:
   ```
   Name: atlas-ai-backend
   Region: Oregon (US West) - or closest to you
   Branch: master
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**:
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Key: `GROQ_API_KEY`
   - Value: `your_groq_api_key_here` (paste your actual key)
   
   - Add another:
   - Key: `GROQ_MODEL`
   - Value: `llama-3.3-70b-versatile`

5. **Select Free Plan**: Choose "Free" instance type

6. **Click "Create Web Service"**

7. **Wait for deployment** (3-5 minutes). You'll see:
   ```
   ==> Build successful!
   ==> Starting service...
   INFO:     Uvicorn running on http://0.0.0.0:10000
   ```

8. **Copy Backend URL**: Something like `https://atlas-ai-backend-xxxxx.onrender.com`

### 3️⃣ Deploy Frontend (Streamlit)

1. **Create Another Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect same GitHub repo

2. **Configure Frontend Service**:
   ```
   Name: atlas-ai-frontend
   Region: Same as backend
   Branch: master
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false
   ```

3. **Add Environment Variable**:
   - Key: `API_BASE_URL`
   - Value: `https://atlas-ai-backend-xxxxx.onrender.com` (use your backend URL from step 2.8)

4. **Select Free Plan**: Choose "Free" instance type

5. **Click "Create Web Service"**

6. **Wait for deployment** (3-5 minutes)

7. **Access Your App**: Click the URL like `https://atlas-ai-frontend-xxxxx.onrender.com`

---

## 🧪 Test Document Upload

1. **Open your frontend URL** in browser

2. **Go to "Operations Copilot" module**

3. **Upload a test document**:
   - Click "Upload SOPs" expander
   - Upload any PDF/DOCX/TXT file (or use `data/sops/sample_sop.txt`)
   - Click "Process Documents"
   - Wait for "Processed: [filename]" success message

4. **Test the AI**:
   - Enable "Demo Mode" checkbox
   - Click a sample question OR type your own
   - AI should respond using the uploaded document context!

---

## ⚡ Quick Verification

After deployment, test these endpoints:

**Backend Health Check**:
```bash
curl https://your-backend-url.onrender.com/api/v1/health
# Should return: {"status": "healthy", ...}
```

**API Documentation**:
Visit: `https://your-backend-url.onrender.com/docs`

**Frontend Access**:
Visit: `https://your-frontend-url.onrender.com`

---

## 🐛 Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify `GROQ_API_KEY` is set correctly
- Ensure build command completed successfully

### Frontend can't connect to backend
- Check `API_BASE_URL` environment variable
- Make sure backend URL is correct (copy from backend service)
- Backend must be fully deployed first

### Document upload fails
- Check backend logs for errors
- Verify file size < 10MB (Render free tier limit)
- Ensure file type is PDF/DOCX/TXT

### App sleeps after 15 minutes (free tier)
- This is normal for Render free tier
- App wakes up on first request (takes ~30 seconds)
- Upgrade to paid plan ($7/month) for always-on

---

## 💰 Cost Breakdown

**Free Tier** (What you get):
- ✅ 750 hours/month per service (31 days = 744 hours)
- ✅ Backend: Free
- ✅ Frontend: Free
- ✅ HTTPS included
- ⚠️ Sleeps after 15 min inactivity

**Paid Plan** ($7/month per service):
- ✅ Always-on (no sleep)
- ✅ More memory/CPU
- ✅ Priority support

**Recommendation**: Start with free tier, upgrade backend if needed.

---

## 🎯 Next Steps

1. ✅ Deploy to Render (you just did this!)
2. 📄 Test document upload functionality
3. 🎥 Record demo video showing:
   - Dashboard with SCADA data
   - Document upload → AI query
   - Incident analysis
   - DGA diagnostics
4. 📝 Add live URLs to your capstone documentation
5. 🚀 Submit project!

---

## 📚 Additional Resources

- **Render Docs**: https://render.com/docs
- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

**Your project is production-ready! 🎉**
