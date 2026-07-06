# 🚀 Render Deployment Guide for Smart-Sheet AI

This project is set up to support quick and easy deployment on [Render](https://render.com). You can choose between the **Automated Blueprint (Recommended)** method, which sets up everything in one go, or the **Manual Configuration** method if you prefer to configure each service manually.

---

## 🛠️ Prerequisites
Before starting, ensure you have:
1. A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
2. A **GitHub Repository** containing this codebase.

---

## ⚡ Option A: Automated Blueprint Deployment (Recommended)
This is the fastest method. Render will read the `render.yaml` file in the project root and automatically provision the PostgreSQL database, Flask API, and React frontend with all configurations pre-linked.

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New** (top right) and select **Blueprint**.
3. Connect your GitHub repository (`jain-sarvagya/Smart-Sheet-AI-Flask`).
4. Give your Blueprint group a name (e.g., `smart-sheet-stack`).
5. Render will detect the `render.yaml` file and show the components to be created:
   * **Database**: `smart-sheet-db` (PostgreSQL)
   * **Backend**: `smart-sheet-backend` (Flask Web Service)
   * **Frontend**: `smart-sheet-frontend` (React Static Site)
6. Under the **Service Variables** prompt:
   * Enter your `GEMINI_API_KEY` (obtained from Google AI Studio).
7. Click **Apply**. Render will deploy all three services. Once finished, you will receive a public URL for your React frontend!

---

## 📝 Option B: Manual Configuration
If you prefer to configure each service separately in the Render Dashboard, follow these steps to fill out the Render forms:

### Step 1: Create a PostgreSQL Database
1. In Render, click **New** and select **PostgreSQL**.
2. Set the **Name** to `smart-sheet-db`.
3. Choose the **Free** tier (or any tier you prefer).
4. Click **Create Database**.
5. Once created, copy the **Internal Database URL** (for backend communication) or the **External Database URL**.

---

### Step 2: Create the Backend Web Service
1. Click **New** and select **Web Service**.
2. Connect your GitHub repository.
3. Configure the fields as follows:
   * **Name**: `Smart-Sheet-AI` (or `smart-sheet-backend`)
   * **Language**: `Python 3`
   * **Branch**: `main`
   * **Region**: `Oregon (US West)` (matching your other services)
   * **Root Directory**: `backend` ⚠️ *(Crucial: This tells Render to run commands inside the backend folder)*
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn run:app` ⚠️ *(Crucial: Notice this is `run:app` because our entrypoint file is `run.py`)*
4. Under **Environment Variables**, click **Add Environment Variable** and add:
   * `FLASK_ENV` = `production`
   * `DATABASE_URL` = `(Paste the Internal Database URL you copied in Step 1)`
   * `GEMINI_API_KEY` = `(Your Google Gemini API Key)`
   * `SECRET_KEY` = `(Enter a random secure string)`
   * `JWT_SECRET_KEY` = `(Enter another random secure string)`
   * `UPLOAD_FOLDER` = `uploads`
5. Click **Create Web Service**. Copy the backend's deployment URL (e.g. `https://smart-sheet-backend.onrender.com`) once it finishes deploying.

---

### Step 3: Create the Frontend Static Site
1. Click **New** and select **Static Site**.
2. Connect your GitHub repository.
3. Configure the fields as follows:
   * **Name**: `smart-sheet-frontend`
   * **Root Directory**: `frontend` ⚠️ *(Crucial: Tells Render to run commands inside the frontend folder)*
   * **Build Command**: `npm install && npm run build`
   * **Publish Directory**: `dist`
4. Under **Environment Variables**, click **Add Environment Variable**:
   * `VITE_API_URL` = `https://your-smart-sheet-backend.onrender.com/api` ⚠️ *(Replace with your actual backend URL from Step 2, and ensure it ends with `/api`)*
5. **Handling React Router (SPA Refresh 404s)**:
   * Navigate to the **Redirects/Rewrites** tab for your frontend static site in the Render dashboard.
   * Add a new rule:
     * **Source Route**: `/*`
     * **Destination**: `/index.html`
     * **Action**: `Rewrite`
   * Save the rule.
6. Click **Create Static Site**.

Your smart-sheet application is now fully deployed!
