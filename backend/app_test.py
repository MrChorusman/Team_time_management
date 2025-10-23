from flask import Flask

# Crear aplicación Flask simple
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from test app!'

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Test app is running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
