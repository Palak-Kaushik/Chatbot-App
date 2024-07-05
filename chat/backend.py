from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from transformers import LlamaForCausalLM, LlamaTokenizer
import sqlite3
from transformers import GPT2LMHeadModel, GPT2Tokenizer


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'JWT_SECRET_KEY'
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# using gpt2 llm
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Database 
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            sender TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        conn.commit()

init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    
    return jsonify(message="User registered successfully"), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
    
    if user and bcrypt.check_password_hash(user[0], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message="Invalid credentials"), 401

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    user_message = data['message']
    current_user = get_jwt_identity()

    try:
        input_text = user_message
        input_ids = tokenizer(input_text, return_tensors="pt").input_ids
        outputs = model.generate(input_ids, max_length=75)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        ai_response = translated_text

        # Save message to database
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username=?', (current_user,))
            user_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO messages (user_id, message, sender) VALUES (?, ?, ?)', (user_id, user_message, 'user'))
            cursor.execute('INSERT INTO messages (user_id, message, sender) VALUES (?, ?, ?)', (user_id, ai_response, 'bot'))
            conn.commit()

    except Exception as e:
        ai_response = f"An error occurred: {str(e)}"

    return jsonify({"message": ai_response, "user": current_user})

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify(message="Logged out successfully"), 200

@app.route('/chat/history', methods=['GET'])
@jwt_required()
def chat_history():
    current_user = get_jwt_identity()

    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT message, sender FROM messages WHERE user_id = (SELECT id FROM users WHERE username = ?)', (current_user,))
            chat_history = [{"text": row[0], "sender": row[1]} for row in cursor.fetchall()]
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify(messages=chat_history), 200

if __name__ == '__main__':
    app.run(debug=True)

