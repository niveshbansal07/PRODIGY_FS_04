from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta
import pymysql
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Database connection helper
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE'],
        cursorclass=pymysql.cursors.DictCursor
    )

# User to socket mapping
user_sockets = {}
socket_users = {}

# JWT helper functions
def create_jwt_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(seconds=app.config['JWT_EXPIRATION_DELTA'])
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create JWT token
        token = create_jwt_token(user_id, email)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {'id': user_id, 'name': name, 'email': email}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        token = create_jwt_token(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid token'}), 401
    
    token = token.replace('Bearer ', '')
    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id != %s ORDER BY name", (payload['user_id'],))
        users = cursor.fetchall()
        conn.close()
        
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid token'}), 401
    
    token = token.replace('Bearer ', '')
    payload = verify_jwt_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    other_user_id = request.args.get('user_id')
    if not other_user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.message, m.created_at,
                   u1.name as sender_name, u2.name as receiver_name
            FROM messages m
            JOIN users u1 ON m.sender_id = u1.id
            JOIN users u2 ON m.receiver_id = u2.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) 
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
        """, (payload['user_id'], other_user_id, other_user_id, payload['user_id']))
        messages = cursor.fetchall()
        conn.close()
        
        # Convert datetime to string
        for msg in messages:
            if isinstance(msg['created_at'], datetime):
                msg['created_at'] = msg['created_at'].isoformat()
        
        return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect(auth=None):
    token = auth.get('token') if auth else None
    if not token:
        disconnect()
        return False
    
    payload = verify_jwt_token(token)
    if not payload:
        disconnect()
        return False
    
    user_id = payload['user_id'] 
    socket_id = request.sid
    
    # Map user to socket
    user_sockets[user_id] = socket_id
    socket_users[socket_id] = user_id
    
    # Notify other users
    socketio.emit('user_online', {'user_id': user_id}, skip_sid=socket_id)
    
@socketio.on('disconnect')
def handle_disconnect():
    socket_id = request.sid
    user_id = socket_users.pop(socket_id, None)
    
    if user_id:
        user_sockets.pop(user_id, None)
        socketio.emit('user_offline', {'user_id': user_id})

@socketio.on('send_message')
def handle_message(data):
    token = data.get('token')
    if not token:
        emit('error', {'message': 'Missing token'})
        return
    
    payload = verify_jwt_token(token)
    if not payload:
        emit('error', {'message': 'Invalid or expired token'})
        return
    
    sender_id = payload['user_id']
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    
    if not receiver_id or not message:
        emit('error', {'message': 'Missing receiver_id or message'})
        return
    
    try:
        # Store message in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
            (sender_id, receiver_id, message)
        )
        message_id = cursor.lastrowid
        cursor.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.message, m.created_at,
                   u1.name as sender_name, u2.name as receiver_name
            FROM messages m
            JOIN users u1 ON m.sender_id = u1.id
            JOIN users u2 ON m.receiver_id = u2.id
            WHERE m.id = %s
        """, (message_id,))
        message_data = cursor.fetchone()
        conn.commit()
        conn.close()
        
        # Convert datetime to string
        if isinstance(message_data['created_at'], datetime):
            message_data['created_at'] = message_data['created_at'].isoformat()
        
        # Send to receiver if online
        receiver_socket = user_sockets.get(receiver_id)
        if receiver_socket:
            socketio.emit('new_message', message_data, room=receiver_socket)
        
        # Send confirmation to sender
        emit('message_sent', message_data)
        
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)