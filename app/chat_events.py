from flask import request
from flask_socketio import emit, join_room
from . import socketio
from .models import CHAT_MESSAGES, salvar_banco

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room in CHAT_MESSAGES:
        emit('history', CHAT_MESSAGES[room], to=request.sid)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg_data = {
        'sender': data['username'],
        'msg': data['message'],
        'is_psico': data.get('is_psico', False)
    }
    
    if room not in CHAT_MESSAGES:
        CHAT_MESSAGES[room] = []
    
    CHAT_MESSAGES[room].append(msg_data)
    
    # Salva o chat no arquivo
    salvar_banco()
    
    emit('receive_message', msg_data, room=room)