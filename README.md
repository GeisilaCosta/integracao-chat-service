# integracao-chat-service
# IntegrAção Chat Service

## 🚀 Serviço de Chat em Tempo Real

Este é o serviço de chat em Python para a plataforma IntegrAção, desenvolvido com Flask e SocketIO.

## 📋 Funcionalidades

- ✅ Chat em tempo real com WebSockets
- ✅ Múltiplas salas de chat
- ✅ Bot inteligente para suporte
- ✅ Histórico de mensagens
- ✅ Indicador de digitação
- ✅ Analytics do chat
- ✅ API REST para integração

## 🛠️ Configuração no Windows

### 1. Instalar Python
- Baixe Python 3.8+ do site oficial: https://python.org
- Durante a instalação, marque "Add Python to PATH"
- Verifique: `python --version`

### 2. Criar Ambiente Virtual
```bash
# Navegar para a pasta do projeto
cd integracao-chat-service

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Executar o Serviço
```bash
python app.py
```

O serviço será executado em: http://localhost:5000

## 🔗 Endpoints da API

### Health Check
```
GET /health
```

### Salas de Chat
```
GET /api/chat/rooms
```

### Histórico de Mensagens
```
GET /api/chat/history/<room_id>
```

### Analytics do Chat
```
GET /api/chat/analytics
```

## 🔌 Eventos WebSocket

### Cliente para Servidor
- `join_room`: Entrar em uma sala
- `send_message`: Enviar mensagem
- `typing`: Indicar que está digitando

### Servidor para Cliente
- `connected`: Confirmação de conexão
- `room_joined`: Confirmação de entrada na sala
- `new_message`: Nova mensagem recebida
- `user_joined`: Usuário entrou na sala
- `user_left`: Usuário saiu da sala
- `user_typing`: Usuário está digitando

## 🤖 Bot Inteligente

O bot responde automaticamente na sala "support" com:
- Informações sobre a plataforma
- Instruções de uso
- Respostas sobre segurança
- Direcionamento para suporte humano

## 📊 Analytics

O serviço fornece métricas em tempo real:
- Total de mensagens
- Usuários ativos
- Mensagens por sala
- Atividade por hora

## 🔧 Integração com Frontend

### Instalar Socket.IO Client
```bash
npm install socket.io-client
```

### Exemplo de Uso
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// Conectar
socket.on('connect', () => {
  console.log('Conectado ao chat!');
});

// Entrar em sala
socket.emit('join_room', {
  room_id: 'general',
  username: 'Meu Nome'
});

// Enviar mensagem
socket.emit('send_message', {
  room_id: 'general',
  message: 'Olá pessoal!',
  username: 'Meu Nome'
});

// Receber mensagens
socket.on('new_message', (message) => {
  console.log('Nova mensagem:', message);
});
```

## 🚀 Deploy

### Desenvolvimento
```bash
python app.py
```

### Produção (com Gunicorn)
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:5000
```

## 📁 Estrutura do Projeto

```
integracao-chat-service/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências Python
├── README.md          # Documentação
└── .env               # Variáveis de ambiente (opcional)
```

## 🔒 Segurança

- CORS configurado para permitir frontend
- Validação de mensagens
- Rate limiting (implementar em produção)
- Sanitização de dados

## 🐛 Troubleshooting

### Erro de porta em uso
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Ou usar porta diferente
python app.py --port 5001
```

### Problemas com WebSocket
- Verificar firewall
- Testar com curl: `curl http://localhost:5000/health`
- Verificar logs no console

### Dependências
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📈 Monitoramento

### Logs
O serviço gera logs detalhados no console:
- Conexões/desconexões
- Mensagens enviadas
- Erros e exceções

### Métricas
Acesse `/api/chat/analytics` para métricas em tempo real.

---

**Desenvolvido com ❤️ para o projeto IntegrAção**

