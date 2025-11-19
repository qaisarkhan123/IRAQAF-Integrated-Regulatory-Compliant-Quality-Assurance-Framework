import time
import urllib.request
time.sleep(2)
try:
    resp = urllib.request.urlopen('http://localhost:8504/', timeout=5)
    print(' SUCCESS: Flask app is responding!')
    print(f'Status Code: {resp.status}')
except Exception as e:
    print(f' FAILED: {e}')
