from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import base64
import os
import json
import tempfile

app = Flask(__name__)
CORS(app)

def get_ydl_opts_with_cookies():
    """Load Instagram cookies from environment variable if available"""
    cookies_json = os.getenv('INSTAGRAM_COOKIES')
    
    base_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    if cookies_json:
        try:
            cookies = json.loads(cookies_json)
            
            # Create temporary cookies file
            temp_cookies = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            
            # Convert JSON cookies to Netscape format
            temp_cookies.write("# Netscape HTTP Cookie File\n")
            for cookie in cookies:
                if cookie.get('name') and cookie.get('value'):
                    domain = cookie.get('domain', '.instagram.com')
                    path = cookie.get('path', '/')
                    secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                    expires = str(cookie.get('expirationDate', 0)).split('.')[0]
                    name = cookie['name']
                    value = cookie['value']
                    
                    temp_cookies.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
            
            temp_cookies.close()
            
            base_opts['cookiefile'] = temp_cookies.name
            print(f"Instagram cookies loaded successfully from {temp_cookies.name}", flush=True)
            
        except json.JSONDecodeError:
            # Try simple sessionid format
            if cookies_json.startswith('sessionid=') or len(cookies_json) > 20:
                temp_cookies = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                temp_cookies.write("# Netscape HTTP Cookie File\n")
                
                sessionid = cookies_json.replace('sessionid=', '').strip()
                temp_cookies.write(f".instagram.com\tTRUE\t/\tTRUE\t0\tsessionid\t{sessionid}\n")
                temp_cookies.close()
                
                base_opts['cookiefile'] = temp_cookies.name
                print(f"Instagram sessionid loaded successfully", flush=True)
            else:
                print("Failed to parse INSTAGRAM_COOKIES", flush=True)
        except Exception as e:
            print(f"Error loading cookies: {str(e)}", flush=True)
    
    return base_opts

def format_error_message(error_str):
    """Convert technical yt-dlp errors to user-friendly messages"""
    error_lower = error_str.lower()
    
    if 'unable to extract' in error_lower or 'empty media response' in error_lower:
        return "This video may be restricted, private, or deleted. Please try a different public video."
    elif 'rate-limit' in error_lower or 'too many requests' in error_lower:
        return "Instagram rate limit reached. Please wait a few minutes and try again."
    elif 'login required' in error_lower or 'not available' in error_lower:
        return "This video requires authentication or is not publicly available."
    elif 'video not found' in error_lower or '404' in error_lower:
        return "Video not found. It may have been deleted or the URL is incorrect."
    else:
        return f"Unable to download video: {error_str}"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'video-download-api'
    })

@app.route('/download-audio-base64', methods=['POST'])
def download_audio_base64():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        print(f"Downloading audio from: {url}", flush=True)
        
        # Get yt-dlp options with cookies
        ydl_opts = get_ydl_opts_with_cookies()
        
        # Extract video info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                
                # Extract metadata
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'creator': info.get('uploader', info.get('channel', 'Unknown')),
                    'creator_handle': info.get('uploader_id', info.get('channel_id', '')),
                    'views': info.get('view_count', 0),
                    'likes': info.get('like_count', 0),
                    'comments': info.get('comment_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'platform': info.get('extractor_key', '').lower()
                }
                
                print(f"Metadata extracted: {metadata['title']} by @{metadata['creator_handle']}", flush=True)
                
            except Exception as e:
                error_msg = str(e)
                friendly_error = format_error_message(error_msg)
                print(f"Download error: {error_msg}", flush=True)
                return jsonify({
                    'success': False,
                    'error': friendly_error,
                    'technical_error': error_msg
                }), 400
        
        # Now download the audio
        with tempfile.TemporaryDirectory() as temp_dir:
            output_template = os.path.join(temp_dir, 'audio')
            
            download_opts = ydl_opts.copy()
            download_opts['outtmpl'] = output_template
            download_opts['format'] = 'bestaudio/best'
            
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                try:
                    ydl.download([url])
                except Exception as e:
                    error_msg = str(e)
                    friendly_error = format_error_message(error_msg)
                    print(f"Download error: {error_msg}", flush=True)
                    return jsonify({
                        'success': False,
                        'error': friendly_error,
                        'technical_error': error_msg
                    }), 400
            
            # Find the downloaded audio file
            audio_files = [f for f in os.listdir(temp_dir) if f.startswith('audio')]
            
            if not audio_files:
                return jsonify({
                    'success': False,
                    'error': 'Audio file not found after download'
                }), 500
            
            audio_path = os.path.join(temp_dir, audio_files[0])
            
            # Check file size (16MB limit for Whisper)
            file_size = os.path.getsize(audio_path)
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb > 16:
                return jsonify({
                    'success': False,
                    'error': f'Audio file too large ({file_size_mb:.1f}MB). Maximum size is 16MB.'
                }), 400
            
            # Read and encode audio file
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Determine MIME type from file extension
            file_ext = os.path.splitext(audio_path)[1].lower()
            mime_types = {
                '.mp3': 'audio/mpeg',
                '.m4a': 'audio/mp4',
                '.webm': 'audio/webm',
                '.opus': 'audio/opus',
                '.ogg': 'audio/ogg',
                '.wav': 'audio/wav'
            }
            mime_type = mime_types.get(file_ext, 'audio/mpeg')
            
            print(f"Audio downloaded successfully: {file_size_mb:.2f}MB ({mime_type})", flush=True)
            
            return jsonify({
                'success': True,
                'audio_base64': audio_base64,
                'mime_type': mime_type,
                'file_size_mb': round(file_size_mb, 2),
                'metadata': metadata
            })
    
    except Exception as e:
        error_msg = str(e)
        friendly_error = format_error_message(error_msg)
        print(f"Unexpected error: {error_msg}", flush=True)
        return jsonify({
            'success': False,
            'error': friendly_error,
            'technical_error': error_msg
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
