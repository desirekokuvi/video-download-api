# Python Video Download API - Deployment Guide

This guide will walk you through deploying your Python video download API to Railway (free tier).

## What This API Does

- Downloads videos from Instagram, TikTok, YouTube, and 1000+ other sites
- Extracts audio from videos
- Returns direct download links
- No file storage needed - just provides URLs

## Step-by-Step Deployment on Railway

### 1. Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email

### 2. Prepare Your Code

All the files are already created in the `/home/ubuntu/python-video-api/` folder:
- `app.py` - Main Flask server
- `requirements.txt` - Python dependencies
- `Procfile` - Tells Railway how to run the app
- `runtime.txt` - Specifies Python version
- `.gitignore` - Files to ignore

### 3. Push to GitHub

**Option A: Using GitHub Desktop (Easiest)**
1. Download [GitHub Desktop](https://desktop.github.com/)
2. Create a new repository called `video-download-api`
3. Add all files from `/home/ubuntu/python-video-api/`
4. Commit and push to GitHub

**Option B: Using Command Line**
```bash
cd /home/ubuntu/python-video-api
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/video-download-api.git
git push -u origin main
```

### 4. Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `video-download-api` repository
5. Railway will automatically detect it's a Python app
6. Click "Deploy"

### 5. Get Your API URL

1. Once deployed, click on your project
2. Go to "Settings" tab
3. Scroll to "Domains"
4. Click "Generate Domain"
5. Copy the URL (e.g., `https://video-download-api-production.up.railway.app`)

### 6. Test Your API

Open your browser or use curl to test:

```bash
# Health check
curl https://YOUR-API-URL.railway.app/health

# Download video
curl -X POST https://YOUR-API-URL.railway.app/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 7. Provide API URL to Manus Integration

Once your API is deployed and working:
1. Copy your Railway API URL
2. Give it to me (the AI assistant)
3. I'll integrate it into your Manus app
4. Full Instagram/TikTok/YouTube download functionality restored!

## Cost

- **Railway Free Tier**: $5 credit per month (enough for ~10,000 video downloads)
- **After free tier**: ~$0.0005 per video download
- **Total**: Essentially free for most use cases

## Troubleshooting

### Build Failed
- Check Railway logs for errors
- Make sure all files are in the repository root
- Verify `requirements.txt` and `Procfile` are present

### API Returns 500 Error
- Check Railway logs: Dashboard → Deployments → View Logs
- Common issue: yt-dlp needs updating (Railway auto-updates on redeploy)

### Video Download Fails
- Some platforms block certain IPs
- Try different video URL
- Check if platform requires authentication

## Alternative Deployment Options

If Railway doesn't work, you can also deploy to:
- **Render.com** (similar to Railway, free tier)
- **Heroku** (requires credit card, but free tier available)
- **Fly.io** (free tier available)

All use the same files - just connect your GitHub repo!

## Security Notes

- API has CORS enabled (allows requests from any domain)
- No authentication required (you can add API key later if needed)
- No file storage (videos are not saved on server)
- Stateless (no database needed)

## Next Steps

After deployment:
1. Test the API with various video URLs
2. Provide the API URL to integrate with Manus app
3. Monitor usage in Railway dashboard
4. Upgrade plan if you exceed free tier limits

---

**Need Help?** If you get stuck at any step, just ask! I can guide you through each part.
