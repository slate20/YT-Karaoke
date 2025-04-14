import os
import sys
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from googleapiclient.discovery import build
import threading
import time
from screeninfo import get_monitors
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Handle PyInstaller's special _MEIPASS directory for bundled resources
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as bundled executable
    bundle_dir = sys._MEIPASS
    # For bundled app, use the parent directory of the executable for config
    # This ensures the config is saved outside the bundled resources
    exe_dir = os.path.dirname(sys.executable)
    CONFIG_FILE = os.path.join(exe_dir, 'config.json')
    print(f"Using executable directory config file: {CONFIG_FILE}")
else:
    # Configuration file path when running as script
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    print(f"Using script config file: {CONFIG_FILE}")

# Function to load configuration
def load_config():
    default_config = {"youtube_api_key": ""}
    
    # Print the config file path for debugging
    print(f"Attempting to load config from: {CONFIG_FILE}")
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                print(f"Successfully loaded config from: {CONFIG_FILE}")
                # Check if the API key exists in the loaded config
                if 'youtube_api_key' in loaded_config:
                    print(f"API key found in config: {'*' * 5}{loaded_config['youtube_api_key'][-4:] if loaded_config['youtube_api_key'] else 'empty'}")
                else:
                    print("No API key found in config, adding empty key")
                    loaded_config['youtube_api_key'] = ""
                return loaded_config
        except Exception as e:
            print(f"Error loading config: {e}")
            print(f"Will create a new default config")
    else:
        # Create a default config file if it doesn't exist
        print(f"Config file not found, creating default at: {CONFIG_FILE}")
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        # Create the config file with default values
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file at: {CONFIG_FILE}")
    except Exception as e:
        print(f"Error creating default config: {e}")
    
    return default_config

# Function to save configuration
def save_config(config):
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Write the config file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
            
        print(f"Successfully saved config to: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Load configuration
config = load_config()

# YouTube API setup
def initialize_youtube_api():
    api_key = config.get('youtube_api_key', '')
    if not api_key:
        return None
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Error initializing YouTube API: {e}")
        return None

youtube = initialize_youtube_api()

# Global variables
singers = []
queue = []
current_song = None
player_window = None
player_thread = None
player_running = False
selected_display = None

# Initialize the player browser
def initialize_player():
    global player_window, player_running, selected_display
    
    options = webdriver.ChromeOptions()
    
    # Add fullscreen argument directly to Chrome options
    options.add_argument("--start-fullscreen")
    
    # Add Linux-specific Chrome options for stability
    if os.name == 'posix':  # Check if running on Linux
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-software-rasterizer")
    
    # Set initial window position before browser opens if display is selected
    if selected_display is not None:
        try:
            # Set window position via Chrome options
            options.add_argument(f"--window-position={selected_display['x']},{selected_display['y']}")
            
            # For Linux, add window size to match the display
            if os.name == 'posix':
                options.add_argument(f"--window-size={selected_display['width']},{selected_display['height']}")
            
            # Create the undetected Chrome driver with positioned options
            player_window = uc.Chrome(options=options)
            
            # Explicitly set window position and size after browser creation for Linux
            if os.name == 'posix':
                player_window.set_window_position(selected_display['x'], selected_display['y'])
                player_window.set_window_size(selected_display['width'], selected_display['height'])
            
            # Load the player page
            player_window.get('http://localhost:5000/player')
            player_running = True
            
            # Additional method to ensure fullscreen if the argument doesn't work
            # This uses JavaScript to request fullscreen mode
            time.sleep(2)  # Wait for page to load
            
            # Move to correct display before fullscreen (especially important for Linux)
            if os.name == 'posix':
                player_window.set_window_position(selected_display['x'], selected_display['y'])
                time.sleep(0.5)  # Short delay to ensure window has moved
            
            player_window.execute_script("document.documentElement.requestFullscreen();")
            
        except Exception as e:
            print(f"Error positioning window: {e}")
            # Fall back to default behavior
            player_window = uc.Chrome(options=webdriver.ChromeOptions().add_argument("--start-fullscreen"))
            player_window.get('http://localhost:5000/player')
            player_running = True
    else:
        # Default behavior if no display selected
        player_window = uc.Chrome(options=options)
        player_window.get('http://localhost:5000/player')
        player_running = True

# Player control thread - handles ad skipping, popup dismissal, and keeps player alive
def player_control_thread():
    global player_window, player_running
    
    while player_running:
        try:
            # 1. Check for skip ad button and click it if available
            handle_skip_ad_button()
            
            # 2. Check for "No thanks" popup and dismiss it
            handle_no_thanks_popup()
            
        except Exception as e:
            # Ignore any errors that might occur during button handling
            pass
            
        # Sleep briefly before checking again
        time.sleep(1)

# Function to handle skip ad buttons
def handle_skip_ad_button():
    if not player_window:
        return
        
    # Using the exact selector found in the YouTube player
    skip_button_selectors = [
        ".ytp-skip-ad-button",                  # Exact class from inspection
        "#skip-button\\:i",                     # Exact ID from inspection (escaped colon)
        ".ytp-ad-skip-button-container button",  # Fallback: container button
        "button[aria-label*='Skip']",           # Fallback: any button with 'Skip' in aria-label
        "button.ytp-ad-skip-button-modern"       # Fallback: modern skip button
    ]
    
    for selector in skip_button_selectors:
        try:
            # Wait for skip button with a short timeout
            skip_button = WebDriverWait(player_window, 0.5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Try multiple methods to click the button
            try:
                # Method 1: Standard Selenium click
                skip_button.click()
                print("Skipped ad using Selenium click")
            except:
                try:
                    # Method 2: JavaScript click (more reliable in some cases)
                    player_window.execute_script("arguments[0].click();", skip_button)
                    print("Skipped ad using JavaScript click")
                except:
                    # Method 3: Direct JavaScript execution to find and click skip button
                    player_window.execute_script("""
                        const skipButtons = [
                            document.querySelector('.ytp-skip-ad-button'),
                            document.querySelector('#skip-button\\:i'),
                            document.querySelector('.ytp-ad-skip-button-container button'),
                            Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Skip'))
                        ];
                        
                        for (const btn of skipButtons) {
                            if (btn) {
                                btn.click();
                                console.log('Skipped ad via direct JavaScript');
                                break;
                            }
                        }
                    """)
                    print("Attempted to skip ad using direct JavaScript")
            
            # Exit the loop if we found a button to click
            break
        except:
            # Button not found or not clickable yet, continue to next selector
            pass

# Function to handle "No thanks" popups
def handle_no_thanks_popup():
    if not player_window:
        return
        
    # Selectors for "No thanks" buttons
    no_thanks_selectors = [
        # Exact selector from the provided HTML
        ".yt-spec-button-shape-next--text span[role='text']:contains('No thanks')",
        "button.yt-spec-button-shape-next:contains('No thanks')",
        # More general selectors
        "button:contains('No thanks')",
        "a:contains('No thanks')",
        "[aria-label='No thanks']",
        # Try to find by text content
        "//button[contains(text(), 'No thanks')]",  # XPath
        "//span[contains(text(), 'No thanks')]/ancestor::button"  # XPath for nested text
    ]
    
    # Try CSS selectors first
    for selector in no_thanks_selectors[:5]:  # First 5 are CSS selectors
        try:
            no_thanks_button = WebDriverWait(player_window, 0.5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Try to click it
            try:
                no_thanks_button.click()
                print("Dismissed 'No thanks' popup using Selenium click")
                return
            except:
                try:
                    player_window.execute_script("arguments[0].click();", no_thanks_button)
                    print("Dismissed 'No thanks' popup using JavaScript click")
                    return
                except:
                    pass
        except:
            pass
    
    # Try XPath selectors
    for selector in no_thanks_selectors[5:]:  # Last 2 are XPath
        try:
            no_thanks_button = WebDriverWait(player_window, 0.5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            try:
                no_thanks_button.click()
                print("Dismissed 'No thanks' popup using Selenium click (XPath)")
                return
            except:
                try:
                    player_window.execute_script("arguments[0].click();", no_thanks_button)
                    print("Dismissed 'No thanks' popup using JavaScript click (XPath)")
                    return
                except:
                    pass
        except:
            pass
    
    # Direct JavaScript approach as a last resort
    try:
        player_window.execute_script("""
            // Try to find and click any "No thanks" button
            const findAndClickNoThanksButton = () => {
                // Method 1: Find by text content
                const allButtons = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                const noThanksButton = allButtons.find(el => {
                    const text = el.textContent.toLowerCase().trim();
                    return text === 'no thanks' || text === 'no, thanks';
                });
                
                if (noThanksButton) {
                    noThanksButton.click();
                    console.log('Clicked No thanks button via JavaScript text search');
                    return true;
                }
                
                // Method 2: Find by aria-label
                const ariaButton = document.querySelector('[aria-label="No thanks"]');
                if (ariaButton) {
                    ariaButton.click();
                    console.log('Clicked No thanks button via aria-label');
                    return true;
                }
                
                return false;
            };
            
            return findAndClickNoThanksButton();
        """)
    except:
        pass

# Routes
@app.route('/')
def index():
    # Check if YouTube API key is configured
    if not config.get('youtube_api_key'):
        return redirect(url_for('settings', first_time=True))
    
    # Check if request is coming from a mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent
    
    # Redirect to mobile version if on a mobile device
    if is_mobile:
        return redirect(url_for('mobile_controls'))
    
    return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global youtube  # Only need global for youtube since we reassign it
    
    api_key_status = None
    error_message = None
    first_time = request.args.get('first_time') == 'True'
    
    if request.method == 'POST':
        new_api_key = request.form.get('youtube_api_key', '').strip()
        
        if new_api_key:
            # Test the API key before saving
            try:
                test_youtube = build('youtube', 'v3', developerKey=new_api_key)
                test_youtube.search().list(q='test', part='snippet', maxResults=1).execute()
                
                # API key is valid, save it
                config['youtube_api_key'] = new_api_key
                save_config(config)
                
                # Reinitialize the YouTube API with the new key
                youtube = build('youtube', 'v3', developerKey=new_api_key)
                
                api_key_status = 'success'
            except HttpError as e:
                error_message = f"Invalid API key or API quota exceeded: {str(e)}"
                api_key_status = 'error'
            except (ValueError, TypeError) as e:
                error_message = f"Error testing API key: {str(e)}"
                api_key_status = 'error'
        else:
            error_message = "API key cannot be empty"
            api_key_status = 'error'
    
    # If it's the first time and no API key is set, show a message
    if first_time and not config.get('youtube_api_key'):
        error_message = "Please set up your YouTube API key to use the application"
        api_key_status = 'error'
    
    return render_template('settings.html', 
                          current_api_key=config.get('youtube_api_key', ''),
                          api_key_status=api_key_status,
                          error_message=error_message)

@app.route('/player')
def player():
    return render_template('player.html')

# Mobile routes
@app.route('/mobile')
def mobile_controls():
    return render_template('mobile_controls.html', active_page='controls')

@app.route('/mobile/queue')
def mobile_queue():
    return render_template('mobile_queue.html', active_page='queue')

@app.route('/mobile/search')
def mobile_search():
    return render_template('mobile_search.html', active_page='search')

# API endpoints
@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'items': []})
    
    # Check if YouTube API is initialized
    if not youtube:
        return jsonify({
            'error': True,
            'message': 'YouTube API key not configured. Please go to settings to configure your API key.'
        }), 400
    
    # Add 'karaoke' to the search query if not already present
    if 'karaoke' not in query.lower():
        query += ' karaoke'
    
    try:
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
    except HttpError as e:
        error_message = str(e)
        if 'API key not valid' in error_message or 'quota' in error_message.lower():
            return jsonify({
                'error': True,
                'message': 'Invalid YouTube API key or quota exceeded. Please check your API key in settings.'
            }), 400
        else:
            return jsonify({
                'error': True,
                'message': f'YouTube API error: {error_message}'
            }), 400
    except (ValueError, TypeError, ConnectionError) as e:
        return jsonify({
            'error': True,
            'message': f'Error searching videos: {str(e)}'
        }), 500

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

@app.route('/api/queue', methods=['GET', 'POST', 'DELETE', 'PUT'])
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
        queue_index = data.get('index', -1)
        
        if 0 <= queue_index < len(queue):
            queue.pop(queue_index)
            socketio.emit('queue_update', {'queue': queue})
            return jsonify({'success': True, 'queue': queue})
        
        return jsonify({'success': False, 'message': 'Invalid queue index'})
        
    elif request.method == 'PUT':
        # Handle reordering the queue
        data = request.json
        from_index = data.get('fromIndex')
        to_index = data.get('toIndex')
        
        if from_index is None or to_index is None:
            return jsonify({'success': False, 'message': 'Missing fromIndex or toIndex'})
        
        if 0 <= from_index < len(queue) and 0 <= to_index < len(queue):
            # Move the item from from_index to to_index
            item = queue.pop(from_index)
            queue.insert(to_index, item)
            socketio.emit('queue_update', {'queue': queue})
            return jsonify({'success': True, 'queue': queue})
        
        return jsonify({'success': False, 'message': 'Invalid queue indices'})

# Player controls
@app.route('/api/player/start', methods=['POST'])
def start_player():
    global player_thread, player_running, selected_display, player_window
    
    # Get display selection from request if available
    data = request.json
    if data and 'display_id' in data and data.get('display_id') is not None:
        try:
            display_id = int(data.get('display_id'))
            monitors = get_monitors()
            
            # Find the selected display
            if 0 <= display_id < len(monitors):
                monitor = monitors[display_id]
                selected_display = {
                    'x': monitor.x,
                    'y': monitor.y,
                    'width': monitor.width,
                    'height': monitor.height,
                    'is_primary': monitor.is_primary if hasattr(monitor, 'is_primary') else (display_id == 0)
                }
                print(f"Selected display {display_id}: {selected_display}")
            else:
                print(f"Invalid display ID: {display_id}, defaulting to primary display")
                selected_display = None
        except Exception as e:
            print(f"Error selecting display: {e}")
            selected_display = None
    else:
        # If no display_id provided, use primary display
        selected_display = None
    
    # Close existing player window if it exists
    if player_window is not None:
        try:
            player_window.quit()
        except Exception as e:
            print(f"Error closing existing player window: {e}")
        finally:
            player_window = None
    
    # Initialize new player window
    initialize_player()
    
    # Start player control thread if not already running
    if player_thread is None or not player_thread.is_alive():
        player_running = True
        player_thread = threading.Thread(target=player_control_thread)
        player_thread.daemon = True
        player_thread.start()
    
    # Emit a socket event to notify clients that the player is running
    socketio.emit('player_status', {
        'running': True,
        'has_current_song': current_song is not None
    })
    
    return jsonify({'success': True})

@app.route('/api/player/stop', methods=['POST'])
def stop_player():
    global player_running, player_window, player_thread, selected_display
    
    player_running = False
    
    # Close the browser window if it exists
    if player_window:
        try:
            player_window.quit()
        except:
            pass  # Ignore errors if browser already closed
        finally:
            # Reset the player_window variable so we can create a new one later
            player_window = None
    
    # Reset the thread variable
    if player_thread and player_thread.is_alive():
        try:
            player_thread.join(timeout=1)  # Wait for thread to finish with timeout
        except:
            pass
    player_thread = None
    
    # Reset the selected display
    selected_display = None
    
    # Emit a socket event to notify clients that the player is stopped
    socketio.emit('player_status', {
        'running': False,
        'has_current_song': False
    })
    
    return jsonify({'success': True})

@app.route('/api/player/next', methods=['POST'])
def next_song():
    global current_song, queue
    
    if queue:
        # Get the next song from the queue without playing it
        current_song = queue.pop(0)
        socketio.emit('queue_update', {'queue': queue})
        socketio.emit('current_song_update', {'current_song': current_song})
        
        # Load the song without playing it and disable autoplay
        video_id = current_song['video_id']
        player_window.get(f'https://www.youtube.com/watch?v={video_id}&noautoplay=1')
        
        # Additional measure to disable autoplay by setting YouTube's autoplay toggle off
        try:
            # Wait for the player to load
            time.sleep(1)
            
            # Try to find and disable autoplay toggle if it's enabled
            # This targets the autoplay toggle button which has a specific class
            script = """
            (function() {
                // Attempt to disable autoplay toggle if it's on
                var autoplayToggle = document.querySelector('paper-toggle-button[aria-label="Autoplay is on"]');
                if (autoplayToggle) {
                    // If autoplay is on, click to turn it off
                    autoplayToggle.click();
                    return 'Autoplay disabled';
                }
                return 'Autoplay already disabled or toggle not found';
            })();
            """
            result = player_window.execute_script(script)
            print(f"Autoplay control: {result}")
        except Exception as e:
            print(f"Error controlling autoplay: {e}")
    
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

@app.route('/api/player/restart', methods=['POST'])
def restart_song():
    global current_song
    
    if player_window and current_song:
        # Reload the current video to restart it with autoplay disabled
        video_id = current_song['video_id']
        player_window.get(f'https://www.youtube.com/watch?v={video_id}&autoplay=1&noautoplay=1&loop=0')
        
        # Emit socket event to notify clients
        socketio.emit('player_action', {'action': 'restart'})
        
        # Additional measure to disable autoplay
        try:
            # Wait for the player to load
            time.sleep(1)
            
            # Try to find and disable autoplay toggle if it's enabled
            script = """
            (function() {
                var autoplayToggle = document.querySelector('paper-toggle-button[aria-label="Autoplay is on"]');
                if (autoplayToggle) {
                    autoplayToggle.click();
                    return 'Autoplay disabled';
                }
                return 'Autoplay already disabled or toggle not found';
            })();
            """
            result = player_window.execute_script(script)
            print(f"Autoplay control: {result}")
        except Exception as e:
            print(f"Error controlling autoplay: {e}")
    
    return jsonify({'success': True})

@app.route('/api/player/toggle_mute', methods=['POST'])
def toggle_mute():
    if player_window:
        # Toggle mute using keyboard 'm' key (YouTube's mute shortcut)
        actions = ActionChains(player_window)
        actions.send_keys('m')
        actions.perform()
        
        # Attempt to get mute state (this may not always work reliably due to YouTube's UI)
        try:
            is_muted = player_window.execute_script(
                "return document.querySelector('.video-stream').muted"
            )
            return jsonify({'success': True, 'muted': is_muted})
        except:
            # If we can't determine state, just return success
            pass
    
    return jsonify({'success': True})

# API endpoint to get player status
@app.route('/api/player/status', methods=['GET'])
def get_player_status():
    return jsonify({
        'success': True,
        'running': player_window is not None and player_running,
        'has_current_song': current_song is not None
    })

# API endpoint to get display information
@app.route('/api/displays', methods=['GET'])
def get_displays():
    try:
        monitors = get_monitors()
        displays = []
        
        for i, monitor in enumerate(monitors):
            displays.append({
                'id': i,
                'name': f"Display {i+1}",
                'width': monitor.width,
                'height': monitor.height,
                'x': monitor.x,
                'y': monitor.y,
                'is_primary': monitor.is_primary if hasattr(monitor, 'is_primary') else (i == 0)
            })
        
        return jsonify({
            'success': True,
            'displays': displays
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# SocketIO events
@socketio.on('connect')
def handle_connect():
    socketio.emit('singers_update', {'singers': singers})
    socketio.emit('queue_update', {'queue': queue})
    if current_song:
        socketio.emit('current_song_update', {'current_song': current_song})

if __name__ == '__main__':
    socketio.run(app, debug=True)