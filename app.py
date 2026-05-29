from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

app = Flask(__name__)

def extract_video_id(url_or_id):
    """
    Extracts the 11-character YouTube video ID from a URL or returns it 
    if it's already an ID.
    """
    # Regex to match various YouTube URL formats (watch, youtu.be, embed, etc.)
    pattern = r'(?:v=|\/|youtu\.be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url_or_id)
    
    if match:
        return match.group(1)
    
    # If no match but it's exactly 11 characters, assume it's a raw video ID
    if len(url_or_id) == 11:
        return url_or_id
        
    return None

@app.route('/get-transcript', methods=['GET'])
def get_transcript():
    video_input = request.args.get('video')
    
    if not video_input:
        return jsonify({"error": "No video URL or ID provided. Use ?video=YOUR_URL"}), 400
        
    video_id = extract_video_id(video_input)
    if not video_id:
        return jsonify({"error": "Invalid YouTube video ID or URL"}), 400
        
    try:
        # Fetch the transcript directly from YouTube's internal caption system (No API key needed)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine the transcript dictionary into a single clean text string
        formatter = TextFormatter()
        full_text = formatter.format_transcript(transcript_list)
        
        # Clean up line breaks for better readability
        clean_text = full_text.replace('\n', ' ')
        
        return jsonify({
            "success": True,
            "video_id": video_id,
            "transcript": clean_text
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Transcript might be disabled for this video, or it is unavailable."
        }), 500

if __name__ == '__main__':
    # Run the app locally on port 5000
    app.run(host='0.0.0.0', port=5000)
