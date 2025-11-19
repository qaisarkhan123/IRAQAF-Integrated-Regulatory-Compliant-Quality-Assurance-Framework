from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'L1 Hub OK', 200

if __name__ == '__main__':
    print('Starting Flask on 127.0.0.1:8504')
    try:
        app.run(host='127.0.0.1', port=8504, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f'Error: {e}')
