#!/usr/bin/env python3
"""
Live PyBoy Screen Capture Server
Captures game window and serves via HTTP
"""

import os
import sys
import time
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Try to import screenshot tools
try:
    from PIL import Image
    HAS_PIL = True
except:
    HAS_PIL = False
    print("Warning: Pillow not available")

# Global state
latest_frame = None
frame_count = 0

def capture_screenshot():
    """Capture PyBoy window using macOS screencapture."""
    global latest_frame, frame_count
    
    output_path = Path("/Users/myassistant/.openclaw/workspace/aether-sync/screen_live.jpg")
    
    # Use macOS screencapture to grab PyBoy window
    # -w flag captures specific window by name
    os.system(f'screencapture -w "PyBoy" "{output_path}" 2>/dev/null || screencapture "{output_path}"')
    
    if output_path.exists():
        frame_count += 1
        latest_frame = output_path
        print(f"📸 Captured frame {frame_count}")
        return True
    return False

def capture_loop():
    """Continuously capture screenshots."""
    print("🎥 Starting capture loop...")
    while True:
        capture_screenshot()
        time.sleep(2)  # Capture every 2 seconds

class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom handler for dashboard with live updates."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/Users/myassistant/.openclaw/workspace/aether-sync", **kwargs)
    
    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            status = {
                'frame_count': frame_count,
                'latest_frame': '/screen_live.jpg' if latest_frame else None,
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(status).encode())
            return
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        pass  # Suppress log spam

def start_server():
    """Start HTTP server."""
    server = HTTPServer(('0.0.0.0', 8081), DashboardHandler)
    print("🌐 Server running on http://0.0.0.0:8081")
    server.serve_forever()

def main():
    # Start capture in background
    capture_thread = threading.Thread(target=capture_loop, daemon=True)
    capture_thread.start()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
