from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import logging

app = Flask(__name__)
CORS(app)  # Allow requests from your Manus app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "video-download-api"})

@app.route('/download', methods=['POST'])
def download_video():
    """
    Download video from URL and return direct download link
    
    Request body:
    {
        "url": "https://www.instagram.com/reel/...",
        "format": "best"  # optional
    }
    
    Response:
    {
        "success": true,
        "video_url": "https://direct-link-to-video.mp4",
        "audio_url": "https://direct-link-to-audio.m4a",
        "title": "Video Title",
        "duration": 30,
        "thumbnail": "https://thumbnail-url.jpg"
    }
    """
    try:
        data = request.json
        video_url = data.get('url')
        format_type = data.get('format', 'best')
        
        if not video_url:
            return jsonify({"success": False, "error": "URL is required"}), 400
        
        logger.info(f"Processing video URL: {video_url}")
        
        # yt-dlp options
        ydl_opts = {
            'format': format_type,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        # Extract video info without downloading
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Get the best video and audio URLs
            video_direct_url = info.get('url')
            
            # Try to get separate audio URL if available
            audio_url = None
            if 'requested_formats' in info:
                for fmt in info['requested_formats']:
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt.get('url')
                        break
            
            response_data = {
                "success": True,
                "video_url": video_direct_url,
                "audio_url": audio_url or video_direct_url,
                "title": info.get('title', 'Unknown'),
                "duration": info.get('duration', 0),
                "thumbnail": info.get('thumbnail', ''),
                "platform": info.get('extractor', 'unknown'),
                "description": info.get('description', '')[:500] if info.get('description') else ''
            }
            
            logger.info(f"Successfully processed: {info.get('title')}")
            return jsonify(response_data)
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to download video: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/extract-audio', methods=['POST'])
def extract_audio_only():
    """
    Extract only audio from video URL
    
    Request body:
    {
        "url": "https://www.youtube.com/watch?v=..."
    }
    
    Response:
    {
        "success": true,
        "audio_url": "https://direct-link-to-audio.m4a",
        "title": "Video Title",
        "duration": 30
    }
    """
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({"success": False, "error": "URL is required"}), 400
        
        logger.info(f"Extracting audio from: {video_url}")
        
        # yt-dlp options for audio only
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            audio_url = info.get('url')
            
            response_data = {
                "success": True,
                "audio_url": audio_url,
                "title": info.get('title', 'Unknown'),
                "duration": info.get('duration', 0),
                "platform": info.get('extractor', 'unknown')
            }
            
            logger.info(f"Successfully extracted audio: {info.get('title')}")
            return jsonify(response_data)
            
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to extract audio: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
