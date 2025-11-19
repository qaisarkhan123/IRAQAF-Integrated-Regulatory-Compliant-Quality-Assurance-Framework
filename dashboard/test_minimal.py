from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'L1 Hub OK', 200

if __name__ == '__main__':
    print('Starting Flask on 0.0.0.0:8504')
    app.run(host='0.0.0.0', port=8504, debug=False, use_reloader=False, threaded=True)
