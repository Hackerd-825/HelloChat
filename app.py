from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
socketio = SocketIO(app, cors_allowed_origins="*")

# 📜 Historique en mémoire
messages_history = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Envoyer l'historique au nouvel utilisateur
    emit('history', messages_history)

@socketio.on('message')
def handle_message(data):
    # data = { "user": "...", "text": "..." }
    messages_history.append(data)

    # Limite à 100 messages pour éviter de trop charger
    if len(messages_history) > 100:
        messages_history.pop(0)

    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
