# Deployment Guide: Sustainable Energy Auditor 🚀

Ready to take your hackathon project live? Follow these steps to deploy the **Frontend** and **Backend** for free.

## 1. Prerequisites
*   A GitHub account.
*   The project code pushed to a GitHub repository.

## 2. Deploy Backend (FastAPI) on Render.com 🐍
Render offers a free tier for web services.

1.  Sign up at [Render.com](https://render.com).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  **Configuration:**
    *   **Name:** `energy-auditor-backend` (or similar)
    *   **Root Directory:** `backend`
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5.  **Environment Variables:**
    Add the keys from your `env.txt` (or local `.env`) here:
    *   `GEMINI_API_KEY`: ...
    *   `AZURE_OPENAI_API_KEY`: ...
    *   `AZURE_OPENAI_ENDPOINT`: ...
    *   `AZURE_OPENAI_DEPLOYMENT_NAME`: ...
    *   `LLM_PROVIDER`: `AZURE` (or `GEMINI`)
6.  Click **Create Web Service**.
    *   Once deployed, copy the URL (e.g., `https://energy-auditor-backend.onrender.com`). You will need this for the frontend!

## 3. Deploy Frontend (React) on Vercel ⚛️
Vercel is the easiest way to deploy Vite/React apps.

1.  Sign up at [Vercel.com](https://vercel.com).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  **Configuration:**
    *   **Framework Preset:** Vite
    *   **Root Directory:** `frontend`
5.  **Environment Variables:**
    *   **Key:** `VITE_API_BASE_URL`
    *   **Value:** Paste your Render Backend URL **without the trailing slash** (e.g., `https://energy-auditor-backend.onrender.com`).
6.  Click **Deploy**.

## 4. Final step
Visit your Vercel URL. You should see the app live! try uploading an image, and it should communicate with your Render backend.

> **Note:** Render free tier spins down after 15 minutes of inactivity. The first request might take ~50 seconds to wake up. Be patient during the demo!
