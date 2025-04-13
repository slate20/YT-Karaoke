import threading
import webview
import time
import os
import sys

# Handle PyInstaller's special _MEIPASS directory for bundled resources
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as bundled executable
    bundle_dir = sys._MEIPASS
    os.chdir(bundle_dir)
    print(f"Running from PyInstaller bundle: {bundle_dir}")

# Import app after setting up the environment
from app import app, socketio

# Global variables
server_thread = None
window = None

def start_server():
    """Start the Flask server in a separate thread"""
    try:
        print("Starting Flask server...")
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    global server_thread, window
    
    print("Starting YouTube Karaoke app...")
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(3)  # Give more time for the server to start
    
    # Create a window with the app
    window = webview.create_window(
        title='YouTube Karaoke', 
        url='http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600),
        text_select=True,
        confirm_close=True,
        background_color='#121212'
    )
    
    # Start the webview application
    webview.start(debug=False)

if __name__ == '__main__':
    main()
