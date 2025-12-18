# Video Download API

Simple Flask API that downloads videos from Instagram, TikTok, YouTube, and 1000+ other platforms using yt-dlp.

## Features

- 🎥 Download videos from Instagram, TikTok, YouTube, and more
- 🎵 Extract audio only
- 🚀 Returns direct download links (no file storage)
- 🔒 CORS enabled for web app integration
- ⚡ Fast and lightweight

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "video-download-api"
}
```

### Download Video
```
POST /download
Content-Type: application/json

{
  "url": "https://www.instagram.com/reel/...",
  "format": "best"  // optional
}
```

Response:
```json
{
  "success": true,
  "video_url": "https://direct-video-url.mp4",
  "audio_url": "https://direct-audio-url.m4a",
  "title": "Video Title",
  "duration": 30,
  "thumbnail": "https://thumbnail.jpg",
  "platform": "instagram",
  "description": "Video description..."
}
```

### Extract Audio Only
```
POST /extract-audio
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=..."
}
```

Response:
```json
{
  "success": true,
  "audio_url": "https://direct-audio-url.m4a",
  "title": "Video Title",
  "duration": 30,
  "platform": "youtube"
}
```

## Supported Platforms

- Instagram (posts, reels, stories)
- TikTok
- YouTube (videos, shorts)
- Twitter/X
- Facebook
- Reddit
- Vimeo
- Dailymotion
- And 1000+ more sites supported by yt-dlp

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

3. Test:
```bash
curl http://localhost:5000/health
```

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions on deploying to Railway, Render, or Heroku.

## Environment Variables

- `PORT` - Server port (default: 5000)

## Tech Stack

- Flask - Web framework
- yt-dlp - Video downloader
- gunicorn - Production server
- flask-cors - CORS support

## License

MIT
