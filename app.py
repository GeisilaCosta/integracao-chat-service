from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import datetime
import uuid
from typing import Dict, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'integracao-chat-secret-2024'

# Configurar CORS para permitir conexões do frontend
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Armazenamento em memória para demonstração
# Em produção, usar Redis ou banco de dados
chat_rooms: Dict[str, Dict] = {}
active_users: Dict[str, Dict] = {}
chat_history: Dict[str, List] = {}

class ChatBot:
    """Bot inteligente para responder perguntas sobre a plataforma"""
    
    def __init__(self):
        self.responses = {
            'saudacao': [
                'Olá! Bem-vindo ao IntegrAção! Como posso ajudá-lo hoje?',
                'Oi! Sou o assistente virtual da plataforma IntegrAção. Em que posso ajudar?',
                'Olá! Estou aqui para esclarecer suas dúvidas sobre nossa plataforma.'
            ],
            'como_funciona': [
                'Nossa plataforma conecta pessoas em vulnerabilidade com apoiadores dispostos a ajudar.',
                'Você pode criar pedidos de ajuda ou ofertas de apoio. Nossa IA faz a conexão ideal!',
                'Funciona assim: cadastre-se, publique sua necessidade ou oferta, e conecte-se com pessoas!'
            ],
            'cadastro': [
                'Para se cadastrar, clique em "Registrar" no menu superior e preencha seus dados.',
                'O cadastro é gratuito! Você pode se registrar como pessoa em vulnerabilidade ou apoiador.',
                'Após o cadastro, você poderá criar seu perfil e começar a usar a plataforma.'
            ],
            'tipos_ajuda': [
                'Oferecemos ajuda em: Moradia, Emprego, Saúde, Educação, Alimentação e muito mais!',
                'Temos categorias para diferentes necessidades: habitação, trabalho, saúde, educação...',
                'Nossa plataforma abrange diversas áreas: moradia, emprego, saúde, educação, alimentação.'
            ],
            'seguranca': [
                'Sua segurança é nossa prioridade! Temos verificação de usuários e sistema de avaliações.',
                'Utilizamos criptografia, verificação de identidade e moderação de conteúdo.',
                'Sistema de avaliações, chat moderado e verificação de perfis garantem sua segurança.'
            ],
            'contato': [
                'Você pode nos contatar pelo formulário na página, email ou este chat!',
                'Estamos disponíveis 24/7 através deste chat ou pelo email contato@integracao.com',
                'Nossa equipe está sempre disponível para ajudar através de múltiplos canais.'
            ],
            'default': [
                'Interessante! Pode me dar mais detalhes sobre sua dúvida?',
                'Entendo. Você pode reformular sua pergunta ou falar com nossa equipe humana?',
                'Vou anotar sua pergunta. Enquanto isso, posso ajudar com informações gerais da plataforma.'
            ]
        }
    
    def get_response(self, message: str) -> str:
        """Analisa a mensagem e retorna uma resposta apropriada"""
        message_lower = message.lower()
        
        # Palavras-chave para diferentes categorias
        keywords = {
            'saudacao': ['oi', 'olá', 'hello', 'ola', 'bom dia', 'boa tarde', 'boa noite'],
            'como_funciona': ['como funciona', 'funciona', 'como usar', 'como', 'funcionalidade'],
            'cadastro': ['cadastro', 'registrar', 'criar conta', 'sign up', 'registro'],
            'tipos_ajuda': ['tipos', 'categorias', 'ajuda', 'moradia', 'emprego', 'saúde', 'educação'],
            'seguranca': ['segurança', 'seguro', 'confiável', 'proteção', 'privacidade'],
            'contato': ['contato', 'falar', 'equipe', 'suporte', 'ajuda humana']
        }
        
        # Encontrar categoria baseada em palavras-chave
        for category, words in keywords.items():
            if any(word in message_lower for word in words):
                import random
                return random.choice(self.responses[category])
        
        # Resposta padrão se não encontrar categoria
        import random
        return random.choice(self.responses['default'])

# Instanciar o bot
chat_bot = ChatBot()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o serviço está funcionando"""
    return jsonify({
        'status': 'healthy',
        'service': 'IntegrAção Chat Service',
        'timestamp': datetime.datetime.now().isoformat(),
        'active_users': len(active_users),
        'active_rooms': len(chat_rooms)
    })

@app.route('/api/chat/rooms', methods=['GET'])
def get_chat_rooms():
    """Retorna lista de salas de chat disponíveis"""
    return jsonify({
        'rooms': [
            {
                'id': 'general',
                'name': 'Chat Geral',
                'description': 'Conversa geral da comunidade',
                'users_count': len([u for u in active_users.values() if u.get('room') == 'general'])
            },
            {
                'id': 'support',
                'name': 'Suporte',
                'description': 'Tire suas dúvidas com nossa equipe',
                'users_count': len([u for u in active_users.values() if u.get('room') == 'support'])
            },
            {
                'id': 'offers',
                'name': 'Ofertas de Ajuda',
                'description': 'Compartilhe e encontre ofertas',
                'users_count': len([u for u in active_users.values() if u.get('room') == 'offers'])
            }
        ]
    })

@app.route('/api/chat/history/<room_id>', methods=['GET'])
def get_chat_history(room_id):
    """Retorna histórico de mensagens de uma sala"""
    history = chat_history.get(room_id, [])
    # Retornar apenas as últimas 50 mensagens
    return jsonify({
        'room_id': room_id,
        'messages': history[-50:] if len(history) > 50 else history
    })

@socketio.on('connect')
def handle_connect():
    """Usuário conectou ao chat"""
    user_id = request.sid
    logger.info(f'Usuário {user_id} conectou')
    
    # Adicionar usuário à lista de ativos
    active_users[user_id] = {
        'id': user_id,
        'connected_at': datetime.datetime.now().isoformat(),
        'room': None
    }
    
    emit('connected', {
        'user_id': user_id,
        'message': 'Conectado com sucesso ao chat IntegrAção!'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Usuário desconectou do chat"""
    user_id = request.sid
    logger.info(f'Usuário {user_id} desconectou')
    
    # Remover usuário da sala atual
    if user_id in active_users:
        current_room = active_users[user_id].get('room')
        if current_room:
            leave_room(current_room)
            socketio.emit('user_left', {
                'user_id': user_id,
                'room': current_room
            }, room=current_room)
        
        # Remover da lista de usuários ativos
        del active_users[user_id]

@socketio.on('join_room')
def handle_join_room(data):
    """Usuário entrou em uma sala"""
    user_id = request.sid
    room_id = data.get('room_id', 'general')
    username = data.get('username', f'Usuário_{user_id[:8]}')
    
    logger.info(f'Usuário {user_id} ({username}) entrando na sala {room_id}')
    
    # Sair da sala anterior se estiver em alguma
    if user_id in active_users and active_users[user_id].get('room'):
        old_room = active_users[user_id]['room']
        leave_room(old_room)
        socketio.emit('user_left', {
            'user_id': user_id,
            'username': username,
            'room': old_room
        }, room=old_room)
    
    # Entrar na nova sala
    join_room(room_id)
    
    # Atualizar informações do usuário
    if user_id in active_users:
        active_users[user_id].update({
            'room': room_id,
            'username': username
        })
    
    # Notificar outros usuários na sala
    socketio.emit('user_joined', {
        'user_id': user_id,
        'username': username,
        'room': room_id,
        'timestamp': datetime.datetime.now().isoformat()
    }, room=room_id)
    
    # Confirmar entrada para o usuário
    emit('room_joined', {
        'room_id': room_id,
        'message': f'Você entrou na sala {room_id}',
        'users_count': len([u for u in active_users.values() if u.get('room') == room_id])
    })

@socketio.on('send_message')
def handle_message(data):
    """Processar mensagem enviada pelo usuário"""
    user_id = request.sid
    room_id = data.get('room_id', 'general')
    message_text = data.get('message', '').strip()
    username = data.get('username', f'Usuário_{user_id[:8]}')
    
    if not message_text:
        return
    
    logger.info(f'Mensagem de {username} na sala {room_id}: {message_text}')
    
    # Criar objeto da mensagem
    message = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'username': username,
        'message': message_text,
        'room_id': room_id,
        'timestamp': datetime.datetime.now().isoformat(),
        'type': 'user'
    }
    
    # Salvar no histórico
    if room_id not in chat_history:
        chat_history[room_id] = []
    chat_history[room_id].append(message)
    
    # Enviar mensagem para todos na sala
    socketio.emit('new_message', message, room=room_id)
    
    # Se for sala de suporte, enviar resposta do bot
    if room_id == 'support':
        bot_response = chat_bot.get_response(message_text)
        
        bot_message = {
            'id': str(uuid.uuid4()),
            'user_id': 'bot',
            'username': 'Assistente IntegrAção',
            'message': bot_response,
            'room_id': room_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'type': 'bot'
        }
        
        # Salvar resposta do bot no histórico
        chat_history[room_id].append(bot_message)
        
        # Enviar resposta do bot após um pequeno delay
        socketio.sleep(1)
        socketio.emit('new_message', bot_message, room=room_id)

@socketio.on('typing')
def handle_typing(data):
    """Usuário está digitando"""
    user_id = request.sid
    room_id = data.get('room_id', 'general')
    username = data.get('username', f'Usuário_{user_id[:8]}')
    is_typing = data.get('is_typing', False)
    
    # Notificar outros usuários na sala
    socketio.emit('user_typing', {
        'user_id': user_id,
        'username': username,
        'is_typing': is_typing
    }, room=room_id, include_self=False)

@app.route('/api/chat/analytics', methods=['GET'])
def get_chat_analytics():
    """Retorna analytics do chat para gráficos"""
    total_messages = sum(len(messages) for messages in chat_history.values())
    
    # Mensagens por sala
    messages_by_room = {
        room: len(messages) for room, messages in chat_history.items()
    }
    
    # Atividade por hora (últimas 24h)
    now = datetime.datetime.now()
    hourly_activity = {}
    
    for hour in range(24):
        hour_start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        hour_key = hour_start.strftime('%H:00')
        hourly_activity[hour_key] = 0
    
    # Contar mensagens por hora
    for messages in chat_history.values():
        for message in messages:
            try:
                msg_time = datetime.datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                if msg_time.date() == now.date():
                    hour_key = msg_time.strftime('%H:00')
                    if hour_key in hourly_activity:
                        hourly_activity[hour_key] += 1
            except:
                continue
    
    return jsonify({
        'total_messages': total_messages,
        'active_users': len(active_users),
        'total_rooms': len(chat_rooms),
        'messages_by_room': messages_by_room,
        'hourly_activity': [
            {'hour': hour, 'messages': count}
            for hour, count in hourly_activity.items()
        ]
    })

if __name__ == '__main__':
    logger.info("Iniciando servidor de chat IntegrAção...")
    logger.info("Acesse: http://localhost:5000")
    logger.info("Health check: http://localhost:5000/health")
    
    # Executar servidor
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        allow_unsafe_werkzeug=True
    )

