from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from transformers import T5Tokenizer, T5ForConditionalGeneration
import sqlite3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# llm init
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

# Database 
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
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
        outputs = model.generate(input_ids, max_length=100)
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        ai_response = translated_text
    except Exception as e:
        ai_response = f"An error occurred: {str(e)}"

    return jsonify({"message": ai_response, "user": current_user})

if __name__ == '__main__':
    app.run(debug=True)
