# Quick Deployment Guide

## Your Files Are Ready! 

All files in `c:\C0C3 Vibe\` are ready to upload.

## Step 1: Create GitHub Repository (2 minutes)

1. Go to: **https://github.com/new**
2. Repository name: **C0C3-Vibe**
3. Make it **Private**
4. **DON'T** check any boxes
5. Click **Create repository**

## Step 2: Upload Files (3 minutes)

After creating the repo, GitHub will show you an empty page.

1. Click the link that says **"uploading an existing file"**
2. Drag these 5 files from `c:\C0C3 Vibe\`:
   - app.py
   - utils.py
   - requirements.txt
   - README.md
   - .gitignore
3. Type commit message: **Initial commit**
4. Click **Commit changes**

## Step 3: Add Config File (1 minute)

1. Click **Add file** → **Create new file**
2. Type filename: **.streamlit/config.toml**
3. Paste this:

```
[theme]
primaryColor = "#00FF00"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
[server]
headless = true
```

4. Click **Commit new file**

## Step 4: Deploy to Streamlit (2 minutes)

1. Go to: **https://share.streamlit.io**
2. Click **Sign in with GitHub**
3. Click **New app**
4. Select your repository: **C0C3-Vibe**
5. Main file: **app.py**
6. Click **Deploy!**

## Done! 🎉

Your app will be live at: `https://c0c3-vibe-xxxxx.streamlit.app`

---

**Your GitHub Token** (use this as password if needed):
```
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
```
