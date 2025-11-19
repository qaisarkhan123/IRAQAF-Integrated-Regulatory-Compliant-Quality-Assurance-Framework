from flask import Flask
import threading
import time
import urllib.request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'L1 Hub OK', 200

def run_app():
    app.run(host='127.0.0.1', port=8504, debug=False, use_reloader=False, threaded=True)

# Start Flask in background thread
thread = threading.Thread(target=run_app, daemon=True)
thread.start()

# Give it time to start
time.sleep(3)

# Test connection
try:
    resp = urllib.request.urlopen('http://localhost:8504/', timeout=5)
    print(' SUCCESS: L1 HUB IS WORKING!')
    print(f'Status: {resp.status}')
except Exception as e:
    print(f' Connection failed: {e}')

# Keep running
time.sleep(100)
