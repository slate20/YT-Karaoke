import os
import json
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from googleapiclient.discovery import build
import threading
import time

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

# YouTube API setup
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Global variables
singers = []
queue = []
current_song = None
player_window = None
player_thread = None
player_running = False

# Initialize the player browser
def initialize_player():
    global player_window, player_running
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # Create the undetected Chrome driver
    player_window = uc.Chrome(options=options)
    player_window.get('http://localhost:5000/player')
    player_running = True

# Player control thread - no longer automatically plays songs
def player_control_thread():
    global player_window, player_running
    
    # This thread now just keeps the player window alive
    while player_running:
        time.sleep(1)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player')
def player():
    return render_template('player.html')

# API endpoints
@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'items': []})
    
    # Add 'karaoke' to the search query if not already present
    if 'karaoke' not in query.lower():
        query += ' karaoke'
    
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=10,
        type='video'
    ).execute()
    
    # Get video durations
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    video_details = youtube.videos().list(
        part='contentDetails',
        id=','.join(video_ids)
    ).execute()
    
    # Create a map of video_id to duration
    duration_map = {}
    for item in video_details['items']:
        duration = item['contentDetails']['duration']
        # Convert ISO 8601 duration to seconds (simplified)
        minutes = 0
        seconds = 0
        if 'M' in duration:
            minutes = int(duration.split('M')[0].split('PT')[1])
        if 'S' in duration:
            seconds = int(duration.split('S')[0].split('M')[-1])
        duration_seconds = minutes * 60 + seconds
        duration_map[item['id']] = duration_seconds
    
    # Add duration to search results
    for item in search_response['items']:
        video_id = item['id']['videoId']
        item['duration'] = duration_map.get(video_id, 0)
    
    return jsonify(search_response)

@app.route('/api/singers', methods=['GET', 'POST', 'DELETE'])
def manage_singers():
    global singers
    
    if request.method == 'GET':
        return jsonify({'singers': singers})
    
    elif request.method == 'POST':
        data = request.json
        singer_name = data.get('name', '').strip()
        
        if singer_name and singer_name not in singers:
            singers.append(singer_name)
            socketio.emit('singers_update', {'singers': singers})
            return jsonify({'success': True, 'singers': singers})
        
        return jsonify({'success': False, 'message': 'Invalid singer name or already exists'})
    
    elif request.method == 'DELETE':
        data = request.json
        singer_name = data.get('name', '')
        
        if singer_name in singers:
            singers.remove(singer_name)
            socketio.emit('singers_update', {'singers': singers})
            return jsonify({'success': True, 'singers': singers})
        
        return jsonify({'success': False, 'message': 'Singer not found'})

@app.route('/api/queue', methods=['GET', 'POST', 'DELETE'])
def manage_queue():
    global queue
    
    if request.method == 'GET':
        return jsonify({'queue': queue})
    
    elif request.method == 'POST':
        data = request.json
        song = {
            'title': data.get('title', ''),
            'singer': data.get('singer', ''),
            'video_id': data.get('video_id', ''),
            'thumbnail': data.get('thumbnail', ''),
            'duration': data.get('duration', 0)
        }
        
        queue.append(song)
        socketio.emit('queue_update', {'queue': queue})
        return jsonify({'success': True, 'queue': queue})
    
    elif request.method == 'DELETE':
        data = request.json
        index = data.get('index', -1)
        
        if 0 <= index < len(queue):
            queue.pop(index)
            socketio.emit('queue_update', {'queue': queue})
            return jsonify({'success': True, 'queue': queue})
        
        return jsonify({'success': False, 'message': 'Invalid queue index'})

# Player controls
@app.route('/api/player/start', methods=['POST'])
def start_player():
    global player_thread, player_running
    
    if player_window is None:
        initialize_player()
    
    if player_thread is None or not player_thread.is_alive():
        player_running = True
        player_thread = threading.Thread(target=player_control_thread)
        player_thread.daemon = True
        player_thread.start()
    
    return jsonify({'success': True})

@app.route('/api/player/stop', methods=['POST'])
def stop_player():
    global player_running
    
    player_running = False
    if player_window:
        player_window.quit()
    
    return jsonify({'success': True})

@app.route('/api/player/next', methods=['POST'])
def next_song():
    global current_song, queue
    
    if queue:
        # Get the next song from the queue without playing it
        current_song = queue.pop(0)
        socketio.emit('queue_update', {'queue': queue})
        socketio.emit('current_song_update', {'current_song': current_song})
        
        # Load the song without playing it
        video_id = current_song['video_id']
        player_window.get(f'https://www.youtube.com/watch?v={video_id}')
    
    return jsonify({'success': True})

@app.route('/api/player/play_pause', methods=['POST'])
def play_pause():
    if player_window:
        # Toggle play/pause using keyboard space key
        
        # Create action chain to press space key (YouTube's play/pause shortcut)
        actions = ActionChains(player_window)
        actions.send_keys(Keys.SPACE)
        actions.perform()
    
    return jsonify({'success': True})

@app.route('/api/player/toggle_fullscreen', methods=['POST'])
def toggle_fullscreen():
    if player_window:
        # Toggle fullscreen using keyboard 'f' key
        
        # Create action chain to press 'f' key (YouTube's fullscreen shortcut)
        actions = ActionChains(player_window)
        actions.send_keys('f')
        actions.perform()
    
    return jsonify({'success': True})

# SocketIO events
@socketio.on('connect')
def handle_connect():
    socketio.emit('singers_update', {'singers': singers})
    socketio.emit('queue_update', {'queue': queue})
    if current_song:
        socketio.emit('current_song_update', {'current_song': current_song})

if __name__ == '__main__':
    socketio.run(app, debug=True)
