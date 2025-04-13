import webview
import time
import sys
import os
import tkinter as tk

def main():
    print("Starting YouTube Karaoke Desktop Client...")
    
    # Get screen resolution
    root = tk.Tk()
    root.withdraw()  # Hide the tkinter window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    
    # Set target resolution (1920x1080)
    target_width = 1920
    target_height = 1080
    
    # Use the smaller of target resolution or screen resolution
    width = min(target_width, screen_width)
    height = min(target_height, screen_height)
    
    print(f"Screen resolution: {screen_width}x{screen_height}")
    print(f"Setting window size to: {width}x{height}")
    
    # Create a window with the app
    window = webview.create_window(
        title='YouTube Karaoke', 
        url='http://127.0.0.1:5000',
        width=width,
        height=height,
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
