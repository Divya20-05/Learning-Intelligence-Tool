# 🚀 Deployment Guide: Public Access

To let reviewers access your tool online without running code, we will deploy it to **Render** (a free cloud platform). It connects directly to your GitHub repository.

## ✅ Prerequisites (Already Done)
- [x] Code pushed to GitHub
- [x] `requirements.txt` updated with `gunicorn`
- [x] Application ready (`app.py`)

---

## 🛠 Step-by-Step Deployment on Render

### 1. Create a Render Account
1. Go to **[render.com](https://render.com)**.
2. Sign up with your **GitHub** account.

### 2. Create a Web Service
1. Click the **"New +"** button and select **"Web Service"**.
2. Select **"Build and deploy from a Git repository"**.
3. Find your repository `Learning-Intelligence-Tool-` and click **"Connect"**.

### 3. Configure the Service
Fill in the following details (leave others as default):

- **Name:** `learning-intelligence-tool` (or any unique name)
- **Region:** `Singapore` (or `Oregon` - closest to you/reviewer)
- **Branch:** `main`
- **Root Directory:** (Leave empty)
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn app:app
  ```
- **Instance Type:** `Free`

### 4. Deploy!
1. Click **"Create Web Service"**.
2. Render will start downloading your code, installing dependencies, and starting the app.
3. Wait about 2-3 minutes. You will see "Live" in green.

---

## 🌍 Accessing Your Tool
Once deployed, Render will give you a public URL (e.g., `https://learning-intelligence-tool.onrender.com`).

**Share this URL with your reviewer!** They can use the web interface exactly like you did locally.

---

## 🔒 Important Note for Reviewers
Since the reviewer might not have your sample data, you can:
1. **Upload the `data/sample_input.csv`** file to the website yourself to test it.
2. Or let them know they can use any CSV with the required columns.

---

## ⚡ Troubleshooting

- **"Build Failed":** Check the logs. Usually a missing dependency.
- **"Application Error":** Check if `gunicorn` is installed (we added it).
- **"Port Error":** Render automatically handles the port validation with `gunicorn`.

---

**That's it! Your AI tool is now live on the internet! 🚀**
