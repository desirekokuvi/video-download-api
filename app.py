from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import logging
import json

app = Flask(__name__)
CORS(app)  # Allow requests from your Manus app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instagram cookie configuration
INSTAGRAM_COOKIES = os.environ.get('INSTAGRAM_COOKIES', '')

def get_ydl_opts_with_cookies(base_opts):
    """Add Instagram cookies to yt-dlp options if available"""
    opts = base_opts.copy()
    
    if INSTAGRAM_COOKIES:
        try:
            # Parse cookies from environment variable (JSON format)
            cookies_data = json.loads(INSTAGRAM_COOKIES)
            
            # Create a temporary cookies file for yt-dlp
            import tempfile
            cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            
            # Write cookies in Netscape format
            cookie_file.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies_data:
                domain = cookie.get('domain', '.instagram.com')
                flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                expiration = str(int(cookie.get('expirationDate', 0)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                cookie_file.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
            
            cookie_file.close()
            opts['cookiefile'] = cookie_file.name
            logger.info("Instagram cookies loaded successfully")
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse INSTAGRAM_COOKIES - using simple string format")
            # Fallback: treat as simple sessionid cookie
            cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            cookie_file.write("# Netscape HTTP Cookie File\n")
            cookie_file.write(f".instagram.com\tTRUE\t/\tTRUE\t0\tsessionid\t{INSTAGRAM_COOKIES}\n")
            cookie_file.close()
            opts['cookiefile'] = cookie_file.name
            logger.info("Instagram sessionid cookie loaded")
        except Exception as e:
            logger.error(f"Error loading Instagram cookies: {str(e)}")
    
    return opts

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
